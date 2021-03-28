// (go version go1.16 linux/amd64)
// monitor & cluster setup : go run raft.go -n <3|5>
// the monitor provides CLI interface for various interactions with the cluster
// the monitor listens at port 1234 & raft servers listen at ports 1235,1236,1237,..

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
	"strconv"
	"strings"
	"sync"
	"time"
)

var N int
var I int
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

type Raft struct {
	Connected   bool
	Role        Role
	CurrentTerm int
	VotedBy     []bool
	Log         []Entry
	CommitIndex int
	NextIndex   []int
	MatchIndex  []int

	follow chan bool
	lead   chan bool
}

func (r *Raft) reset() {
	mux.Lock()
	r.Role = Follower
	r.CurrentTerm = 0
	r.VotedBy = make([]bool, N)
	r.Log = make([]Entry, 1)
	r.Log[0] = Entry{0, 0}
	r.CommitIndex = 0
	r.NextIndex = make([]int, N)
	r.MatchIndex = make([]int, N)
	mux.Unlock()
	r.clearChannels()
	r.follow <- true
	go r.updateMonitorState()
}

type ResetRequest struct{}

type ResetResponse struct{}

func (r *Raft) Reset(req *ResetRequest, res *ResetResponse) error {
	r.reset()
	return nil
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

type AppendEntriesRequest struct {
	Term         int
	LeaderId     int
	PrevLogIndex int
	PrevLogTerm  int
	Entries      []Entry
	LeaderCommit int
}

type AppendEntriesResponse struct {
	Term    int
	Success bool
}

func (r *Raft) AppendEntries(req *AppendEntriesRequest, res *AppendEntriesResponse) error {
	if !r.Connected {
		return errors.New(fmt.Sprintf("Peer %v unavailable", I))
	}
	if req.Term >= r.CurrentTerm {
		res.Term = req.Term
		res.Success = true
		mux.Lock()
		r.CurrentTerm = req.Term
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
		return errors.New(fmt.Sprintf("Peer %v unavailable", I))
	}
	if req.Term > r.CurrentTerm {
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

func (r *Raft) contendCandidecy() {
	mux.Lock()
	defer mux.Unlock()
	r.Role = Candidate
	r.VotedBy = make([]bool, N)
	r.VotedBy[I] = true
	r.CurrentTerm++
}

func (r *Raft) askForVotes() {
	for i := 0; i < N; i++ {
		if i == I {
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
			req.CandidateId = I
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
}

func (r *Raft) sendHeartbeats() {
	for i := 0; i < N; i++ {
		if i == I {
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
			req := new(AppendEntriesRequest)
			res := new(AppendEntriesResponse)
			mux.Lock()
			req.Term = r.CurrentTerm
			req.LeaderId = I
			mux.Unlock()
			err = client.Call("Raft.AppendEntries", req, &res)
			if err != nil {
				return
			}
			mux.Lock()
			if !res.Success && r.Role != Follower {
				mux.Unlock()
				r.becomeFollower()
				r.CurrentTerm = res.Term
				r.clearChannels()
				r.follow <- true
			} else {
				mux.Unlock()
			}
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
			r.sendHeartbeats()
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

// Server initialization

func initializeServer() {
	// initialize global state
	monitorAddr = os.Args[2]
	for i := 6; i < len(os.Args); i++ {
		clusterAddr = append(clusterAddr, os.Args[i])
	}
	N = len(clusterAddr)
	x, xerr := strconv.ParseInt(os.Args[4], 0, 4)
	if xerr != nil {
		panic(xerr)
	}
	I = int(x)
	rand.Seed(int64(I))

	// initialize raft server object
	raft := new(Raft)
	raft.follow = make(chan bool, 1)
	raft.lead = make(chan bool, 1)
	raft.Connected = true
	raft.reset()

	rpc.Register(raft)
	rpc.HandleHTTP()
	l, e := net.Listen("tcp", fmt.Sprintf(":%v", strings.Split(clusterAddr[I], ":")[1]))
	if e != nil {
		panic(e)
	}
	go http.Serve(l, nil)
	raft.run()
}

// Monitor Implementation

type Monitor struct {
	rs []Raft
	rc int
	rt int
}

type RegisterUpdatedServerStateRequest struct {
	I int
	R Raft
}

type RegisterUpdatedServerStateResponse struct{}

func (r *Raft) updateMonitorState() {
	client, err := rpc.DialHTTP("tcp", monitorAddr)
	if err != nil {
		return
	}
	req := new(RegisterUpdatedServerStateRequest)
	res := new(RegisterUpdatedServerStateResponse)
	mux.Lock()
	req.I = I
	req.R = *r
	mux.Unlock()
	go func() {
		err = client.Call("Monitor.RegisterUpdatedServerState", req, &res)
		if err != nil {
			panic(err)
		}
	}()
}

func (m *Monitor) RegisterUpdatedServerState(
	req *RegisterUpdatedServerStateRequest, res *RegisterUpdatedServerStateResponse) error {
	mux.Lock()
	defer mux.Unlock()
	m.rc++
	m.rs[req.I] = req.R
	go m.render()
	return nil
}

func (m *Monitor) render() {
	mux.Lock()
	defer mux.Unlock()
	crt := int(time.Now().Unix())
	if crt-m.rt < 1 {
		return
	}
	m.rt = crt
	fmt.Print("\033[H\033[2J") // https://stackoverflow.com/a/22892171/5664000
	fmt.Println("\nstate ", m.rc)
	for i := 0; i < len(m.rs); i++ {
		fmt.Printf("\nServer %v | %c\n", i, "zabcd"[i])
		fmt.Printf("Term : %v\n", m.rs[i].CurrentTerm)
		fmt.Printf("Role : %v\n", [3]string{"follower", "candidate", "leader"}[m.rs[i].Role])
		fmt.Printf("Network Connectivity : %v\n", m.rs[i].Connected)
		fmt.Printf("Commit Index & Log : %v, %v\n", m.rs[i].CommitIndex, m.rs[i].Log)
		voteSheet := ""
		if m.rs[i].Role != Follower {
			for p := 0; p < N; p++ {
				if m.rs[i].VotedBy[p] {
					voteSheet += fmt.Sprintf("%v, ", p)
				}
			}
			fmt.Printf("Voted By : %v\n", voteSheet[:len(voteSheet)-2])
		}
		if m.rs[i].Role == Leader {
			fmt.Printf("Next Index for peers : %v\n", m.rs[i].NextIndex)
			fmt.Printf("Match Index for peers : %v\n", m.rs[i].MatchIndex)
		}
	}
	fmt.Println()
	fmt.Println("Press Enter to send new log entry to Leader with the highest term (if any)")
	fmt.Println("Press numeric keys [0,1,2,..] to change network connectivity of servers")
	fmt.Println("Press alphabetic keys [z,a,b,..] to reset servers")
	fmt.Println("Press ctrl+c to turndown the processes")
}

// Monitor Initialization

func initializeMonitoredCluster() {
	// initialize global state
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

	// trigger server processes
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	for i := 0; i < N; i++ {
		args := append([]string{"run", "raft.go", "-m", monitorAddr, "-i", fmt.Sprintf("%v", i), "-p"}, clusterAddr...)
		cmd := exec.CommandContext(ctx, "go", args...)
		err := cmd.Start()
		if err != nil {
			panic(err)
		}
	}

	// initialize monitor object & rpc interface
	monitor := new(Monitor)
	monitor.rs = make([]Raft, N)
	monitor.rc = 0
	monitor.rt = 0
	rpc.Register(monitor)
	rpc.HandleHTTP()
	l, e := net.Listen("tcp", fmt.Sprintf(":%v", strings.Split(monitorAddr, ":")[1]))
	if e != nil {
		panic(e)
	}
	go http.Serve(l, nil)

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
		for i, s := range networkChangeInputs {
			if key == s {
				client, err := rpc.DialHTTP("tcp", clusterAddr[i])
				if err != nil {
					return
				}
				req := new(NetworkChangeRequest)
				res := new(NetworkChangeResponse)
				err = client.Call("Raft.NetworkChange", req, &res)
				if err != nil {
					return
				}
			}
		}
		for i, s := range resetInputs {
			if key == s {
				client, err := rpc.DialHTTP("tcp", clusterAddr[i])
				if err != nil {
					return
				}
				req := new(ResetRequest)
				res := new(ResetResponse)
				err = client.Call("Raft.Reset", req, &res)
				if err != nil {
					return
				}
			}
		}
	}
}

func main() {
	if os.Args[1] == "-n" {
		initializeMonitoredCluster()
	} else if os.Args[1] == "-m" {
		initializeServer()
	} else {
		panic("Arguments must strictly follow one of two allowed forms")
	}
}
