// [ Reference ]
//  Publication : In Search of an Understandable Consensus Algorithm (Extended Version)
//              - Ongaro & Ousterhout

// [ Setup ]
// groupadd raft
// for i in {0..4}; do useradd -g raft r$i; mkdir /home/r$i; chown r$i:raft /home/r$i; done

// [ Execution ]
// rustc raft.rs -o /tmp/raft
// for i in {0..4}; do runuser -l r$i -c "/tmp/raft $i > ~/log" & done
// watch -n 0.1 tail -n 3 /home/r*/log

// [ Interaction ]
// iptables -A OUTPUT -m owner -j DROP --uid r$i
// iptables -D OUTPUT -m owner -j DROP --uid r$i
// echo -ne `python3 -c "print(\
// '\\\\\xff'*24\
// +'\\\\\x00'*3+'\\\\\x$t'\
// +'\\\\\x00'*3+'\\\\\x$e'\
// )"` > /dev/tcp/127.0.0.1/789$i

// [ Termination ]
// ps aux | grep /tmp/raft | awk '{print $2}' |  xargs kill

use std::convert::TryInto;
use std::env;
use std::fmt;
use std::io::{Read, Write};
use std::net::{TcpListener, TcpStream};
use std::process;
use std::sync::{Arc, Mutex};
use std::thread::{self, JoinHandle};
use std::time::{Duration, SystemTime, UNIX_EPOCH};

const N: usize = 5;
const ADDR: &str = "127.0.0.1";
const BASE_PORT: usize = 7890;
const TCP_TIMEOUT: Duration = Duration::new(1, 0);
const HEARTBEAT_INTERVAL_SEC: u64 = 1;

#[derive(Debug, Clone, Copy, PartialEq)]
enum State {
    Leader([usize; N], [usize; N]),
    Candidate([bool; N], u32),
    Follower(Option<usize>, bool),
}

impl State {
    fn is_leader(&self) -> bool {
        if let Self::Leader(..) = self {
            true
        } else {
            false
        }
    }

    fn get_next_index(&self, i: usize) -> usize {
        if let Self::Leader(ref next_index, _) = self {
            next_index[i]
        } else {
            1
        }
    }

    fn set_next_index(&mut self, i: usize, v: usize) {
        if let Self::Leader(ref mut next_index, _) = self {
            next_index[i] = v;
        }
    }

    fn decrement_next_index(&mut self, i: usize) {
        if let Self::Leader(ref mut next_index, _) = self {
            if next_index[i] > 1 {
                next_index[i] -= 1;
            }
        }
    }

    fn set_match_index(&mut self, i: usize, v: usize) {
        if let Self::Leader(_, ref mut match_index) = self {
            match_index[i] = v;
        }
    }

    fn get_index_to_commit(&self) -> usize {
        if let Self::Leader(_, ref match_index) = self {
            let mut smi = match_index.clone();
            smi.sort();
            smi[N >> 1]
        } else {
            0
        }
    }

    fn is_candidate(&self) -> bool {
        if let Self::Candidate(..) = self {
            true
        } else {
            false
        }
    }

    fn count_vote(&mut self, i: usize) {
        if let Self::Candidate(ref mut voted_by, _) = self {
            voted_by[i] = true;
        }
    }

    fn has_enough_votes(&self) -> bool {
        if let Self::Candidate(ref voted_by, _) = self {
            voted_by.iter().filter(|&&x| x).count() > N >> 1
        } else {
            false
        }
    }

    fn get_vote_request_attempts(&self) -> u32 {
        if let Self::Candidate(_, vote_request_attempts) = self {
            *vote_request_attempts
        } else {
            0
        }
    }

    fn increment_vote_request_attempts(&mut self) {
        if let Self::Candidate(_, ref mut vote_request_attempts) = self {
            *vote_request_attempts += 1;
        }
    }

    fn reset_vote_request_attempts(&mut self) {
        if let Self::Candidate(_, ref mut vote_request_attempts) = self {
            *vote_request_attempts = 0;
        }
    }

    fn is_follower(&self) -> bool {
        if let Self::Follower(..) = self {
            true
        } else {
            false
        }
    }

    fn heartbeat_received(&self) -> bool {
        if let Self::Follower(_, heartbeat_received) = self {
            *heartbeat_received
        } else {
            false
        }
    }

    fn unset_heartbeat_received(&mut self) {
        if let Self::Follower(_, ref mut heartbeat_received) = self {
            *heartbeat_received = false;
        }
    }

    fn voted_for(&self, i: usize) -> bool {
        if let Self::Follower(Some(ref voted_for), _) = self {
            *voted_for == i
        } else {
            false
        }
    }
}

struct Raft {
    id: usize,
    process_id: u32,
    state: State,
    term: u32,
    log: Vec<(u32, u32)>,
    commit_index: usize,
}

struct AppendEntryRequest {
    id: usize,
    term: u32,
    prev_log_index: usize,
    prev_log_term: u32,
    entry: Option<(u32, u32)>,
    commit_index: usize,
}

struct AppendEntryResponse {
    id: usize,
    term: u32,
    success: bool,
    match_index: usize,
}

struct VoteRequest {
    id: usize,
    term: u32,
    last_log_index: usize,
    last_log_term: u32,
}

struct VoteResponse {
    id: usize,
    term: u32,
    granted: bool,
}

enum Request {
    A(AppendEntryRequest),
    V(VoteRequest),
}

enum Response {
    A(AppendEntryResponse),
    V(VoteResponse),
}

impl Raft {
    fn new(id: usize) -> Raft {
        Raft {
            id: id,
            process_id: process::id(),
            state: State::Follower(None, true),
            term: 0,
            log: vec![(0, 0)],
            commit_index: 0,
        }
    }

    fn init(self) {
        let r = Arc::new(Mutex::new(self));
        Self::start_server(Arc::clone(&r));
        Self::start_logger(Arc::clone(&r));
        Self::r#loop(r);
    }

    fn r#loop(r: Arc<Mutex<Raft>>) {
        let mut wait_ms: u32 = 1 + r.lock().unwrap().id as u32;
        loop {
            let wait_s: u64;
            let mut raft = r.lock().unwrap();
            match raft.state {
                State::Leader(..) => {
                    let join_handle = raft.send_heartbeats(&r);
                    drop(raft);
                    wait_s = if join_handle.join().unwrap() {
                        0
                    } else {
                        HEARTBEAT_INTERVAL_SEC
                    };
                }
                State::Candidate(..) => {
                    raft.request_votes(&r);
                    raft.state.increment_vote_request_attempts();
                    if raft.state.get_vote_request_attempts() > 4 {
                        raft.state.reset_vote_request_attempts();
                        raft.become_candidate();
                    }
                    drop(raft);
                    wait_s = 2 * HEARTBEAT_INTERVAL_SEC;
                }
                State::Follower(..) => {
                    if !raft.state.heartbeat_received() {
                        raft.become_candidate();
                        continue;
                    }
                    raft.state.unset_heartbeat_received();
                    drop(raft);
                    wait_s = 4 * HEARTBEAT_INTERVAL_SEC;
                }
            }
            wait_ms *= 997;
            wait_ms %= 977;
            thread::sleep(Duration::new(wait_s, 1000000 * wait_ms));
        }
    }

    fn become_leader(&mut self) {
        self.state = State::Leader([self.log.len(); N], [0; N]);
        self.state.set_match_index(self.id, self.log.len() - 1);
    }

    fn become_candidate(&mut self) {
        self.state = State::Candidate([false; N], 0);
        self.state.count_vote(self.id);
        self.term += 1;
    }

    fn become_follower(&mut self, leader: Option<usize>, term: u32) {
        self.state = State::Follower(leader, true);
        self.term = term;
    }

    fn send_heartbeats(&self, r: &Arc<Mutex<Raft>>) -> JoinHandle<bool> {
        let mut threads = Vec::new();
        for p in 0..N {
            if p == self.id {
                continue;
            }
            threads.push(Self::send_request(
                Arc::clone(r),
                p,
                Request::A(AppendEntryRequest {
                    id: self.id,
                    term: self.term,
                    prev_log_index: self.state.get_next_index(p) - 1,
                    prev_log_term: self.log[self.state.get_next_index(p) - 1].0,
                    entry: if self.state.get_next_index(p) < self.log.len() {
                        Some(self.log[self.state.get_next_index(p)])
                    } else {
                        None
                    },
                    commit_index: self.commit_index,
                }),
            ));
        }
        thread::spawn(move || {
            let mut immediate_retry_required = false;
            for thread in threads {
                match thread.join() {
                    Ok(Ok(irr)) => immediate_retry_required |= irr,
                    _ => {}
                }
            }
            immediate_retry_required
        })
    }

    fn request_votes(&self, r: &Arc<Mutex<Raft>>) {
        for p in 0..N {
            if p == self.id {
                continue;
            }
            Self::send_request(
                Arc::clone(r),
                p,
                Request::V(VoteRequest {
                    id: self.id,
                    term: self.term,
                    last_log_index: self.log.len() - 1,
                    last_log_term: self.log.last().unwrap().0,
                }),
            );
        }
    }

    fn handle_request(&mut self, req: Request) -> Response {
        match req {
            Request::A(ae_req) => {
                let mut success = false;
                let mut match_index = 0;
                if ae_req.id as u32 == std::u32::MAX {
                    if let Some(entry) = ae_req.entry {
                        self.log.push(entry);
                        if self.state.is_leader() {
                            self.state.set_next_index(self.id, self.log.len());
                            self.state.set_match_index(self.id, self.log.len() - 1);
                        }
                        success = true;
                    }
                } else if self.term < ae_req.term
                    || (self.term == ae_req.term && self.state.is_follower())
                {
                    self.become_follower(Some(ae_req.id), ae_req.term);
                    if self.log.len() > ae_req.prev_log_index
                        && self.log[ae_req.prev_log_index].0 == ae_req.prev_log_term
                    {
                        success = true;
                        match_index = ae_req.prev_log_index;
                        self.commit_index = self
                            .commit_index
                            .max((self.log.len() - 1).min(ae_req.commit_index));
                        if let Some(entry) = ae_req.entry {
                            if self.log.len() == ae_req.prev_log_index + 1 {
                                self.log.push(entry);
                            } else {
                                self.log[ae_req.prev_log_index + 1] = entry;
                            }
                            match_index += 1;
                        }
                    }
                }
                Response::A(AppendEntryResponse {
                    id: self.id,
                    term: self.term,
                    success: success,
                    match_index: match_index,
                })
            }
            Request::V(v_req) => {
                let mut granted = self.term == v_req.term && self.state.voted_for(v_req.id);
                if !granted {
                    let last_log_index = self.log.len() - 1;
                    let last_log_term = self.log.last().unwrap().0;
                    granted = self.term < v_req.term
                        && (last_log_term < v_req.last_log_term
                            || (last_log_term == v_req.last_log_term
                                && last_log_index <= v_req.last_log_index));
                    if granted {
                        self.become_follower(Some(v_req.id), v_req.term);
                    }
                }
                self.term = self.term.max(v_req.term);
                Response::V(VoteResponse {
                    id: self.id,
                    term: self.term,
                    granted: granted,
                })
            }
        }
    }

    fn handle_response(&mut self, res: Response) -> bool {
        let mut immediate_retry_required = false;
        match res {
            Response::A(ae_res) => {
                if ae_res.term < self.term || !self.state.is_leader() {
                    return immediate_retry_required;
                }
                if ae_res.success {
                    self.state.set_match_index(ae_res.id, ae_res.match_index);
                    self.state.set_next_index(ae_res.id, ae_res.match_index + 1);
                    self.commit_index = self.commit_index.max(self.state.get_index_to_commit());
                    immediate_retry_required =
                        self.state.get_next_index(ae_res.id) < self.log.len();
                } else if ae_res.term == self.term {
                    self.state.decrement_next_index(ae_res.id);
                    immediate_retry_required = true;
                } else {
                    self.become_follower(None, ae_res.term);
                }
            }
            Response::V(v_res) => {
                if v_res.term < self.term || !self.state.is_candidate() {
                    return immediate_retry_required;
                }
                if v_res.granted {
                    self.state.count_vote(v_res.id);
                    if self.state.has_enough_votes() {
                        self.become_leader();
                    }
                } else if v_res.term > self.term {
                    self.become_follower(None, v_res.term);
                }
            }
        }
        immediate_retry_required
    }

    fn get_addr(id: usize) -> String {
        let port = BASE_PORT + id;
        format!("{ADDR}:{port}")
    }

    fn start_server(r: Arc<Mutex<Raft>>) -> JoinHandle<()> {
        thread::spawn(move || {
            let listener = TcpListener::bind(Self::get_addr(r.lock().unwrap().id)).unwrap();
            for stream_result in listener.incoming() {
                let r_clone = Arc::clone(&r);
                thread::spawn(move || -> Result<(), std::io::Error> {
                    let mut stream = stream_result.unwrap();
                    stream.set_read_timeout(Some(TCP_TIMEOUT))?;
                    stream.set_write_timeout(Some(TCP_TIMEOUT))?;
                    let mut req = [0 as u8; 32];
                    stream.read(&mut req)?;
                    stream.write(&Self::serialize_response(
                        r_clone
                            .lock()
                            .unwrap()
                            .handle_request(Self::deserialize_request(req)),
                    ))?;
                    Ok(())
                });
            }
        })
    }

    fn send_request(
        r: Arc<Mutex<Raft>>,
        p: usize,
        req: Request,
    ) -> JoinHandle<Result<bool, std::io::Error>> {
        thread::spawn(move || {
            let mut stream =
                TcpStream::connect_timeout(&Self::get_addr(p).parse().unwrap(), TCP_TIMEOUT)?;
            stream.set_read_timeout(Some(TCP_TIMEOUT))?;
            stream.set_write_timeout(Some(TCP_TIMEOUT))?;
            stream.write(&Self::serialize_request(req))?;
            let mut res = [0 as u8; 32];
            stream.read_exact(&mut res)?;
            Ok(r.lock()
                .unwrap()
                .handle_response(Self::deserialize_response(res)))
        })
    }

    fn concat_u8_4_8_arrays(u8_4_8_arrays: [[u8; 4]; 8]) -> [u8; 32] {
        u8_4_8_arrays
            .iter()
            .flat_map(|s| s.iter())
            .cloned()
            .collect::<Vec<u8>>()
            .try_into()
            .unwrap()
    }

    fn serialize_request(req: Request) -> [u8; 32] {
        match req {
            Request::A(a) => Self::concat_u8_4_8_arrays([
                [0xff; 4],
                (a.id as u32).to_be_bytes(),
                a.term.to_be_bytes(),
                (a.prev_log_index as u32).to_be_bytes(),
                a.prev_log_term.to_be_bytes(),
                (a.commit_index as u32).to_be_bytes(),
                match a.entry {
                    Some((t, _)) => t.to_be_bytes(),
                    None => [0x00; 4],
                },
                match a.entry {
                    Some((_, e)) => e.to_be_bytes(),
                    None => [0x00; 4],
                },
            ]),
            Request::V(a) => Self::concat_u8_4_8_arrays([
                [0x00; 4],
                (a.id as u32).to_be_bytes(),
                a.term.to_be_bytes(),
                (a.last_log_index as u32).to_be_bytes(),
                a.last_log_term.to_be_bytes(),
                [0x00; 4],
                [0x00; 4],
                [0x00; 4],
            ]),
        }
    }

    fn deserialize_request(byte_array: [u8; 32]) -> Request {
        if byte_array[0] == 0xff {
            Request::A(AppendEntryRequest {
                id: u32::from_be_bytes(byte_array[4..8].try_into().unwrap()) as usize,
                term: u32::from_be_bytes(byte_array[8..12].try_into().unwrap()),
                prev_log_index: u32::from_be_bytes(byte_array[12..16].try_into().unwrap()) as usize,
                prev_log_term: u32::from_be_bytes(byte_array[16..20].try_into().unwrap()),
                commit_index: u32::from_be_bytes(byte_array[20..24].try_into().unwrap()) as usize,
                entry: if byte_array[24..28] != [0, 0, 0, 0] {
                    Some((
                        u32::from_be_bytes(byte_array[24..28].try_into().unwrap()),
                        u32::from_be_bytes(byte_array[28..32].try_into().unwrap()),
                    ))
                } else {
                    None
                },
            })
        } else {
            Request::V(VoteRequest {
                id: u32::from_be_bytes(byte_array[4..8].try_into().unwrap()) as usize,
                term: u32::from_be_bytes(byte_array[8..12].try_into().unwrap()),
                last_log_index: u32::from_be_bytes(byte_array[12..16].try_into().unwrap()) as usize,
                last_log_term: u32::from_be_bytes(byte_array[16..20].try_into().unwrap()),
            })
        }
    }

    fn serialize_response(res: Response) -> [u8; 32] {
        match res {
            Response::A(a) => Self::concat_u8_4_8_arrays([
                [0xff; 4],
                (a.id as u32).to_be_bytes(),
                a.term.to_be_bytes(),
                if a.success { [0xff; 4] } else { [0x00; 4] },
                (a.match_index as u32).to_be_bytes(),
                [0xff; 4],
                [0xff; 4],
                [0xff; 4],
            ]),
            Response::V(a) => Self::concat_u8_4_8_arrays([
                [0x00; 4],
                (a.id as u32).to_be_bytes(),
                a.term.to_be_bytes(),
                if a.granted { [0xff; 4] } else { [0x00; 4] },
                [0x00; 4],
                [0x00; 4],
                [0x00; 4],
                [0x00; 4],
            ]),
        }
    }

    fn deserialize_response(byte_array: [u8; 32]) -> Response {
        if byte_array[0] == 0xff {
            Response::A(AppendEntryResponse {
                id: u32::from_be_bytes(byte_array[4..8].try_into().unwrap()) as usize,
                term: u32::from_be_bytes(byte_array[8..12].try_into().unwrap()),
                success: byte_array[12] == 0xff,
                match_index: u32::from_be_bytes(byte_array[16..20].try_into().unwrap()) as usize,
            })
        } else {
            Response::V(VoteResponse {
                id: u32::from_be_bytes(byte_array[4..8].try_into().unwrap()) as usize,
                term: u32::from_be_bytes(byte_array[8..12].try_into().unwrap()),
                granted: byte_array[12] == 0xff,
            })
        }
    }

    fn start_logger(r: Arc<Mutex<Raft>>) -> JoinHandle<()> {
        thread::spawn(move || loop {
            println!("{:?}", r.lock().unwrap());
            thread::sleep(Duration::new(1, 0));
        })
    }
}

impl fmt::Debug for Raft {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(
            f,
            "epoch: {:<15?}",
            SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_secs()
        )?;
        write!(f, "process_id: {:<15}", self.process_id)?;
        write!(f, "id: {:<15}", self.id)?;
        write!(f, "term: {:<15}\n", self.term)?;
        write!(f, "commit_index: {:<15}", self.commit_index)?;
        write!(f, "log: {:?}\n", self.log)?;
        write!(f, "state: {:?}", self.state)
    }
}

fn main() {
    Raft::new(
        env::args().collect::<Vec<String>>()[1]
            .parse::<usize>()
            .unwrap(),
    )
    .init();
}
