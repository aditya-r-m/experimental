// monitor & cluster setup : go run raft.go -n <3|5>

// the monitor provides CLI interface for various interactions with the cluster
// the monitor listens at port 1234 & raft servers listen at ports 1235,1236,1237,..

// if there is abnormal termination of monitor, servers may need to be turned down manually
// ps aux | grep raft | awk '{print $2}' | xargs kill

// (go version go1.16 linux/amd64)
// https://raft.github.io/raft.pdf
package main

import (
	"context"
	"errors"
	"fmt"
	"math/rand"
	"net"
	"net/http"
	"net/rpc"
	"os"
	"os/exec"
	"sort"
	"strconv"
	"strings"
	"sync"
	"time"
)

var N int
var monitorAddr string
var clusterAddr []string
var mux sync.Mutex

func getShortTimer() <-chan time.Time {
	return time.After(time.Duration(2) * time.Second)
}

func getLongTimer() <-chan time.Time {
	return time.After(time.Duration(5+rand.Intn(5)) * time.Second)
}

// Raft server Implementation

type Role int

const (
	Follower Role = iota
	Candidate
	Leader
)

type Entry struct {
	Term  int
	Value int
}

var EmptyEntry Entry

type Raft struct {
	I         int
	Connected bool

	Role        Role
	CurrentTerm int
	VotedBy     []bool
	Log         []Entry
	CommitIndex int
	NextIndex   []int
	MatchIndex  []int

	callInProgress []bool
	follow         chan bool
	lead           chan bool
	propagate      chan bool
}

func (r *Raft) clearChannels() {
F:
	for {
		select {
		case <-r.follow:
		default:
			break F
		}
	}
L:
	for {
		select {
		case <-r.lead:
		default:
			break L
		}
	}
P:
	for {
		select {
		case <-r.propagate:
		default:
			break P
		}
	}
}

func (r *Raft) reset() {
	mux.Lock()
	r.Role = Follower
	r.CurrentTerm = 0
	r.VotedBy = make([]bool, N)
	r.Log = make([]Entry, 1)
	r.Log[0] = EmptyEntry
	r.CommitIndex = 0
	r.NextIndex = make([]int, N)
	r.MatchIndex = make([]int, N)
	mux.Unlock()
	r.clearChannels()
	r.follow <- true
	go r.updateMonitorState()
}

// rpc interfaces to provide log entries, reset/disconnect/re-connect raft server nodes

type LogEntryRequest struct {
	Value int
}

type LogEntryResponse struct{}

func (r *Raft) LogEntry(req *LogEntryRequest, res *LogEntryResponse) error {
	if r.Role == Leader {
		mux.Lock()
		r.Log = append(r.Log, Entry{r.CurrentTerm, req.Value})
		r.NextIndex[r.I] = len(r.Log)
		r.MatchIndex[r.I] = len(r.Log) - 1
		mux.Unlock()
		r.clearChannels()
		r.propagate <- true
		go r.updateMonitorState()
	}
	return nil
}

type ResetRequest struct{}

type ResetResponse struct{}

func (r *Raft) Reset(req *ResetRequest, res *ResetResponse) error {
	r.reset()
	return nil
}

type NetworkChangeRequest struct{}

type NetworkChangeResponse struct{}

func (r *Raft) NetworkChange(req *NetworkChangeRequest, res *NetworkChangeResponse) error {
	mux.Lock()
	defer mux.Unlock()
	r.Connected = !r.Connected
	go r.updateMonitorState()
	return nil
}

// raft rpc interfaces

type AppendEntriesRequest struct {
	Term         int
	LeaderId     int
	PrevLogIndex int
	PrevLogTerm  int
	Entry        Entry
	LeaderCommit int
}

type AppendEntriesResponse struct {
	Term    int
	Success bool
}

func (r *Raft) AppendEntries(req *AppendEntriesRequest, res *AppendEntriesResponse) error {
	if !r.Connected {
		return errors.New(fmt.Sprintf("Peer %v unavailable", r.I))
	}
	if req.Term >= r.CurrentTerm {
		res.Term = req.Term
		mux.Lock()
		r.CurrentTerm = req.Term
		if len(r.Log) > req.PrevLogIndex && r.Log[req.PrevLogIndex].Term == req.PrevLogTerm {
			res.Success = true
			if req.Entry != EmptyEntry {
				if len(r.Log) == req.PrevLogIndex+1 {
					r.Log = append(r.Log, EmptyEntry)
				}
				r.Log[req.PrevLogIndex+1] = req.Entry
				r.Log = r.Log[:req.PrevLogIndex+2]
			}
			r.CommitIndex = req.LeaderCommit
			if r.CommitIndex >= len(r.Log) {
				r.CommitIndex = len(r.Log) - 1
			}
		} else {
			res.Success = false
		}
		mux.Unlock()
		r.clearChannels()
		r.follow <- true
	} else {
		mux.Lock()
		res.Term = r.CurrentTerm
		mux.Unlock()
		res.Success = false
	}
	return nil
}

type RequestVoteRequest struct {
	Term         int
	CandidateId  int
	LastLogIndex int
	LastLogTerm  int
}

type RequestVoteResponse struct {
	Term        int
	VoteGranted bool
}

func (r *Raft) RequestVote(req *RequestVoteRequest, res *RequestVoteResponse) error {
	if !r.Connected {
		return errors.New(fmt.Sprintf("Peer %v unavailable", r.I))
	}
	mux.Lock()
	isCandidateLogUpdated := req.LastLogTerm > r.Log[len(r.Log)-1].Term ||
		(req.LastLogTerm == r.Log[len(r.Log)-1].Term && req.LastLogIndex >= len(r.Log)-1)
	mux.Unlock()
	if req.Term > r.CurrentTerm && isCandidateLogUpdated {
		res.Term = req.Term
		res.VoteGranted = true
		mux.Lock()
		r.CurrentTerm = req.Term
		mux.Unlock()
		r.clearChannels()
		r.follow <- true
	} else {
		mux.Lock()
		res.Term = r.CurrentTerm
		mux.Unlock()
		res.VoteGranted = false
	}
	return nil
}

// raft server lifecycle implementation

func (r *Raft) contendCandidecy() {
	mux.Lock()
	defer mux.Unlock()
	r.Role = Candidate
	r.VotedBy = make([]bool, N)
	r.VotedBy[r.I] = true
	r.CurrentTerm++
}

func (r *Raft) askForVotes() {
	for i := 0; i < N; i++ {
		if i == r.I {
			continue
		}
		go func(i int) {
			if !r.Connected {
				return
			}
			client, err := rpc.DialHTTP("tcp", clusterAddr[i])
			if err != nil {
				return
			}
			res := new(RequestVoteResponse)
			req := new(RequestVoteRequest)
			mux.Lock()
			req.Term = r.CurrentTerm
			req.CandidateId = r.I
			req.LastLogIndex = len(r.Log) - 1
			req.LastLogTerm = r.Log[len(r.Log)-1].Term
			mux.Unlock()
			err = client.Call("Raft.RequestVote", req, &res)
			if err != nil {
				return
			}
			mux.Lock()
			r.VotedBy[i] = res.VoteGranted
			c := 0
			for i := 0; i < N; i++ {
				if r.VotedBy[i] {
					c++
				}
			}
			if c > N/2 && r.Role != Leader {
				mux.Unlock()
				r.becomeLeader()
				if len(r.lead) == 0 {
					r.clearChannels()
					r.lead <- true
				}
			} else {
				mux.Unlock()
			}
		}(i)
	}
}

func (r *Raft) becomeLeader() {
	mux.Lock()
	defer mux.Unlock()
	r.Role = Leader
	for i := 0; i < N; i++ {
		r.NextIndex[i] = len(r.Log)
		r.MatchIndex[i] = 0
	}
	r.MatchIndex[r.I] = len(r.Log) - 1
}

func (r *Raft) sendHeartbeatsAndLogsToPeer(i int) {
	if !r.Connected {
		return
	}
	client, err := rpc.DialHTTP("tcp", clusterAddr[i])
	if err != nil {
		return
	}
	done := false
	for !done {
		req := new(AppendEntriesRequest)
		res := new(AppendEntriesResponse)
		mux.Lock()
		req.Term = r.CurrentTerm
		req.LeaderId = r.I
		req.PrevLogIndex = r.NextIndex[i] - 1
		req.PrevLogTerm = r.Log[r.NextIndex[i]-1].Term
		req.Entry = EmptyEntry
		if r.NextIndex[i] < len(r.Log) {
			req.Entry = r.Log[r.NextIndex[i]]
		}
		req.LeaderCommit = r.CommitIndex
		mux.Unlock()
		err = client.Call("Raft.AppendEntries", req, &res)
		if err != nil {
			return
		}
		mux.Lock()
		if res.Term > r.CurrentTerm {
			r.CurrentTerm = res.Term
			mux.Unlock()
			r.becomeFollower()
			r.clearChannels()
			r.follow <- true
			return
		}
		if res.Success {
			r.MatchIndex[i] = req.PrevLogIndex
			sortedMatchIndex := make([]int, N)
			copy(sortedMatchIndex, r.MatchIndex)
			sort.Ints(sortedMatchIndex)
			if sortedMatchIndex[N/2] > r.CommitIndex {
				r.CommitIndex = sortedMatchIndex[N/2]
			}
			if r.NextIndex[i] == len(r.Log) {
				done = true
			} else {
				r.NextIndex[i]++
			}
		} else {
			r.NextIndex[i]--
		}
		mux.Unlock()
	}
}

func (r *Raft) sendHeartbeatsAndLogs() {
	for i := 0; i < N; i++ {
		if i == r.I {
			continue
		}
		go func(i int) {
			mux.Lock()
			if r.callInProgress[i] {
				mux.Unlock()
				return
			}
			r.callInProgress[i] = true
			mux.Unlock()
			r.sendHeartbeatsAndLogsToPeer(i)
			mux.Lock()
			r.callInProgress[i] = false
			mux.Unlock()
		}(i)
	}
}

func (r *Raft) becomeFollower() {
	mux.Lock()
	defer mux.Unlock()
	r.Role = Follower
	r.VotedBy = make([]bool, N)
}

func (r *Raft) followerLoop() {
	for {
		go r.updateMonitorState()
		select {
		case <-getLongTimer():
			r.contendCandidecy()
			return
		case <-r.follow:
		}
	}
}

func (r *Raft) candidateLoop() {
	termTimeout := getLongTimer()
	for {
		go r.updateMonitorState()
		select {
		case <-getShortTimer():
			r.askForVotes()
		case <-termTimeout:
			r.contendCandidecy()
			return
		case <-r.follow:
			r.becomeFollower()
			return
		case <-r.lead:
			r.becomeLeader()
			return
		}
	}
}

func (r *Raft) leaderLoop() {
	for {
		go r.updateMonitorState()
		select {
		case <-getShortTimer():
			r.sendHeartbeatsAndLogs()
		case <-r.propagate:
			r.sendHeartbeatsAndLogs()
		case <-r.follow:
			r.becomeFollower()
			return
		}
	}
}

func (r *Raft) run() {
	for {
		switch r.Role {
		case Follower:
			r.followerLoop()
		case Candidate:
			r.candidateLoop()
		case Leader:
			r.leaderLoop()
		}
	}
}

// Raft server initialization

func initializeServer(i int) {
	raft := new(Raft)

	raft.I = i
	raft.Connected = true

	raft.callInProgress = make([]bool, N)
	raft.follow = make(chan bool, 1)
	raft.lead = make(chan bool, 1)
	raft.propagate = make(chan bool, 1)

	raft.reset()

	rpc.Register(raft)
	rpc.HandleHTTP()
	l, err := net.Listen("tcp", fmt.Sprintf(":%v", strings.Split(clusterAddr[raft.I], ":")[1]))
	if err != nil {
		panic(err)
	}
	go http.Serve(l, nil)
	raft.run()
}

// Monitor Implementation

type Monitor struct {
	servers        []Raft
	stateCounter   int
	lastRenderTime int
	nextLogValue   int
}

type RegisterUpdatedServerStateRequest struct {
	R Raft
}

type RegisterUpdatedServerStateResponse struct{}

func (r *Raft) updateMonitorState() {
	client, err := rpc.DialHTTP("tcp", monitorAddr)
	if err != nil {
		panic(err)
	}
	req := new(RegisterUpdatedServerStateRequest)
	res := new(RegisterUpdatedServerStateResponse)
	mux.Lock()
	req.R = *r
	mux.Unlock()
	err = client.Call("Monitor.RegisterUpdatedServerState", req, &res)
	if err != nil {
		panic(err)
	}
}

func (m *Monitor) RegisterUpdatedServerState(
	req *RegisterUpdatedServerStateRequest, res *RegisterUpdatedServerStateResponse) error {
	mux.Lock()
	defer mux.Unlock()
	m.stateCounter++
	m.servers[req.R.I] = req.R
	go m.render()
	return nil
}

func (m *Monitor) render() {
	mux.Lock()
	defer mux.Unlock()
	crt := int(time.Now().Unix())
	if crt-m.lastRenderTime < 1 {
		return
	}
	m.lastRenderTime = crt
	fmt.Print("\033[H\033[2J") // https://stackoverflow.com/a/22892171/5664000
	for i := 0; i < len(m.servers); i++ {
		if len(m.servers[i].Log) < 1 {
			fmt.Printf("initializing servers...")
			return
		}
	}
	fmt.Println("\nstate ", m.stateCounter)
	for i := 0; i < len(m.servers); i++ {
		fmt.Printf("\nServer %v | %c\n", i, "zabcd"[i])
		fmt.Printf("Term : %v\n", m.servers[i].CurrentTerm)
		fmt.Printf("Role : %v\n", [3]string{"follower", "candidate", "leader"}[m.servers[i].Role])
		if m.servers[i].Connected {
			fmt.Println("\033[1;34mConnected to the cluster\033[0m")
		} else {
			fmt.Println("\033[1;31mDisconnected from the cluster\033[0m")
		}
		fmt.Printf("Commit Index & Log : %v, %v\n", m.servers[i].CommitIndex, m.servers[i].Log)
		voteSheet := ""
		if m.servers[i].Role != Follower {
			for p := 0; p < N; p++ {
				if m.servers[i].VotedBy[p] {
					voteSheet += fmt.Sprintf("%v, ", p)
				}
			}
			fmt.Printf("Voted By : %v\n", voteSheet[:len(voteSheet)-2])
		}
		if m.servers[i].Role == Leader {
			fmt.Printf("Next Index for peers : %v\n", m.servers[i].NextIndex)
			fmt.Printf("Match Index for peers : %v\n", m.servers[i].MatchIndex)
		}
	}
	fmt.Println()
	fmt.Println("The monitor automatically renders updated state at most once per second.")
	fmt.Println("Thus, there can be a slight delay before updates are propagated & rendered.")
	fmt.Println("Additionally, note that Enter key is not required for providing key inputs.")
	fmt.Println("Press Semicolon (;) to send new log entry to Leader with the highest term (if any)")
	fmt.Println("Press numeric keys [0,1,2,..] to change network connectivity of servers")
	fmt.Println("Press alphabetic keys [z,a,b,..] to reset servers")
	fmt.Println("Press ctrl+c to turndown the processes")
}

func (m *Monitor) handleKeyInputs() {
	// Key events setup : https://stackoverflow.com/a/54423725/5664000
	ch := make(chan string)
	go func(ch chan string) {
		// disable input buffering
		exec.Command("stty", "-F", "/dev/tty", "cbreak", "min", "1").Run()
		var b []byte = make([]byte, 1)
		for {
			os.Stdin.Read(b)
			ch <- string(b)
		}
	}(ch)

	networkChangeInputs := append(make([]string, 0), "0", "1", "2")
	resetInputs := append(make([]string, 0), "z", "a", "b")
	if N == 5 {
		networkChangeInputs = append(networkChangeInputs, "3", "4")
		resetInputs = append(resetInputs, "c", "d")
	}
	for {
		key, _ := <-ch
		inputHandled := false
		if key == ";" {
			leaderTerm := 0
			leaderAddress := ""
			for i := 0; i < len(m.servers); i++ {
				if m.servers[i].Role == Leader && m.servers[i].CurrentTerm > leaderTerm {
					leaderTerm = m.servers[i].CurrentTerm
					leaderAddress = clusterAddr[i]
				}
			}
			if leaderTerm > 0 {
				client, err := rpc.DialHTTP("tcp", leaderAddress)
				if err != nil {
					panic(err)
				}
				req := new(LogEntryRequest)
				res := new(LogEntryResponse)
				req.Value = m.nextLogValue
				m.nextLogValue++
				err = client.Call("Raft.LogEntry", req, &res)
				if err != nil {
					panic(err)
				}
				inputHandled = true
			}
		}
		for i, s := range networkChangeInputs {
			if key == s {
				client, err := rpc.DialHTTP("tcp", clusterAddr[i])
				if err != nil {
					panic(err)
				}
				req := new(NetworkChangeRequest)
				res := new(NetworkChangeResponse)
				err = client.Call("Raft.NetworkChange", req, &res)
				if err != nil {
					panic(err)
				}
				inputHandled = true
			}
		}
		for i, s := range resetInputs {
			if key == s {
				client, err := rpc.DialHTTP("tcp", clusterAddr[i])
				if err != nil {
					panic(err)
				}
				req := new(ResetRequest)
				res := new(ResetResponse)
				err = client.Call("Raft.Reset", req, &res)
				if err != nil {
					panic(err)
				}
				inputHandled = true
			}
		}
		if inputHandled {
			mux.Lock()
			m.lastRenderTime = 0
			mux.Unlock()
			go m.render()
		}
	}
}

// Monitor Initialization

func initializeMonitoredCluster() {
	// trigger server processes
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	for i := 0; i < N; i++ {
		args := append([]string{
			"run", "raft.go", "-m", monitorAddr, "-i", fmt.Sprintf("%v", i), "-p"}, clusterAddr...)
		cmd := exec.CommandContext(ctx, "go", args...)
		err := cmd.Start()
		if err != nil {
			panic(err)
		}
	}

	// initialize monitor object & interfaces
	monitor := new(Monitor)
	monitor.servers = make([]Raft, N)
	monitor.stateCounter = 0
	monitor.lastRenderTime = 0
	monitor.nextLogValue = 1
	rpc.Register(monitor)
	rpc.HandleHTTP()
	l, err := net.Listen("tcp", fmt.Sprintf(":%v", strings.Split(monitorAddr, ":")[1]))
	if err != nil {
		panic(err)
	}
	go http.Serve(l, nil)

	monitor.handleKeyInputs()
}

func main() {
	if os.Args[1] == "-n" {
		// initialize global state for monitor
		x, xerr := strconv.ParseInt(os.Args[2], 0, 64)
		if xerr != nil {
			panic(xerr)
		}
		if x != 3 && x != 5 {
			panic("cluster size must be either 3 or 5")
		}
		N = int(x)
		monitorAddr = "localhost:1234"
		for i := 0; i < N; i++ {
			clusterAddr = append(clusterAddr, fmt.Sprintf("localhost:123%v", 5+i))
		}

		// trigger server processes, initialize monitor object & listeners
		initializeMonitoredCluster()
	} else if os.Args[1] == "-m" {
		// initialize global state for server
		monitorAddr = os.Args[2]
		for i := 6; i < len(os.Args); i++ {
			clusterAddr = append(clusterAddr, os.Args[i])
		}
		N = len(clusterAddr)
		x, xerr := strconv.ParseInt(os.Args[4], 0, 4)
		if xerr != nil {
			panic(xerr)
		}
		rand.Seed(int64(x))

		// initialize server object & listeners
		initializeServer(int(x))
	} else {
		panic("Arguments must strictly follow one of two allowed forms")
	}
}
