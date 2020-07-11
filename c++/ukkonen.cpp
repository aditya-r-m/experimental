#include<iostream>
#include<algorithm>
#include<string>
#include<vector>
#include<map>

using namespace std;

const char NULLC = '\0';
const int INF = 100000000;

vector<char> s;

struct Node;
struct Edge {
  int start, length;
  Node *source, *target;
  Edge(int pstart, int plength, Node *psource, Node *ptarget) {
    start = pstart;
    length = plength;
    source = psource;
    target = ptarget;
  }
};

struct Node {
  int id;
  map<char, Edge*> edgeMap;
  Edge *sourceEdge;
  Node *suffixLink;
  Node(int pid) {
    id = pid;
    suffixLink = NULL;
    sourceEdge = NULL;
  }

  void print() {
    cout << "Node " << id << endl;
    cout << "source " << (sourceEdge == NULL ? -1 : sourceEdge->source->id) << endl;
    cout << "suffix link " << (suffixLink == NULL ? -1 : suffixLink->id) << endl;
    for (auto p: edgeMap) {
      cout << "Edge " << p.first << " contains info ";
      cout << "start " << p.second->start << " length " << p.second->length << " text ";
      for (int i = p.second->start; i < min((int) s.size(), p.second->start + p.second->length); i++) cout << s[i];
      cout << " source " << p.second->source->id << " target " << p.second->target->id;
      cout << endl;
    }
  }
};

vector<Node*> nodes;

int remaindr = 0;
Node *activeNode = NULL;
char activeEdgeChar = NULLC;
int activeLength = 0;

Node *lastAddedInternalNode = NULL;

void printState() {
  for (auto node: nodes) {
    node->print();
  }
  cout << "remaindr " << remaindr << " ";
  cout << "activeNode " << (activeNode == NULL ? -1 : activeNode->id) << " ";
  cout << "activeEdgeChar " << activeEdgeChar << " ";
  cout << "activeLength " << activeLength << " ";
  cout << endl << endl;
}

void init() {
  s.clear();
  nodes.clear();
  remaindr = 0;
  activeNode = NULL;
  activeEdgeChar = NULLC;
  activeLength = 0;
  lastAddedInternalNode = NULL;
  nodes.push_back(new Node(0));
}

void extend(char c) {
  int i = s.size();
  s.push_back(c);
  if (!remaindr) remaindr = 1;
  bool done = false;

  while (!done) {
    if (activeNode == NULL) activeNode = nodes[0];
    if (activeEdgeChar == NULLC) activeEdgeChar = c;
    if (activeLength < 0) activeLength = 0;
    Edge *activeEdge = activeNode->edgeMap.count(activeEdgeChar) ? activeNode->edgeMap[activeEdgeChar] : NULL;
    if (activeEdge == NULL) {
      nodes.push_back(new Node(nodes.size()));
      nodes[nodes.size() - 1]->sourceEdge = 
      activeNode->edgeMap[activeEdgeChar] =
        new Edge(i, INF, activeNode, nodes[nodes.size() - 1]);
      remaindr--;
      if (activeNode == nodes[0]) {
        activeNode = NULL;
        activeEdgeChar = NULLC;
        done = true;
      } else {
        if (activeNode->suffixLink != NULL) {
          activeNode = activeNode->suffixLink;
        } else {
          if (activeNode == nodes[0]) activeLength--;
          activeEdgeChar = s[i - activeLength];
          activeNode = nodes[0];
        }
      }
    } else {
      while (activeEdge != NULL && activeLength >= activeEdge->length) {
        activeNode = activeEdge->target;
        activeLength -= activeEdge->length;
        activeEdgeChar = s[i - activeLength];
        activeEdge = activeNode->edgeMap.count(activeEdgeChar) ? activeNode->edgeMap[activeEdgeChar] : NULL;
      }
      if (activeEdge != NULL) {
        if (c == s[activeEdge->start + activeLength]) {
          remaindr++;
          activeLength++;
          done = true;
        } else {
          nodes.push_back(new Node(nodes.size()));
          Node *newInternalNode = nodes[nodes.size() - 1];
          if (lastAddedInternalNode != NULL) lastAddedInternalNode->suffixLink = newInternalNode;
          lastAddedInternalNode = newInternalNode;

          nodes.push_back(new Node(nodes.size()));
          nodes[nodes.size() - 1]->sourceEdge =
          newInternalNode->edgeMap[c] =
            new Edge(i, INF, newInternalNode, nodes[nodes.size() - 1]);
 
          activeEdge->target->sourceEdge =
          newInternalNode->edgeMap[s[activeEdge->start + activeLength]] =
            new Edge(activeEdge->start + activeLength, activeEdge->length - activeLength, newInternalNode, activeEdge->target);

          activeEdge->target = newInternalNode;
          newInternalNode->sourceEdge = activeEdge;

          activeEdge->length = activeLength;
          lastAddedInternalNode = newInternalNode;
          remaindr--;
          if (activeNode->suffixLink != NULL) {
            activeNode = activeNode->suffixLink;
          } else {
            if (activeNode == nodes[0]) activeLength--;
            activeEdgeChar = s[i - activeLength];
            activeNode = nodes[0];
          }
        }
      }
    }
    // cout << "extending phase " << i << s[i] << endl;
    // printState();
  }
  if (lastAddedInternalNode != NULL) {
    Node *n = lastAddedInternalNode;
    Node *p = lastAddedInternalNode->sourceEdge->source;
    Node *sln = p->suffixLink != NULL ? p->suffixLink : nodes[0];
    int l = n->sourceEdge->length;
    if (p == nodes[0]) l--;
    char ec;
    while (l > 0) {
      ec = s[n->sourceEdge->start + n->sourceEdge->length - l];
      sln = sln->edgeMap[ec]->target;
      l -= sln->sourceEdge->length;
    }
    if (sln != n) n->suffixLink = sln;
    lastAddedInternalNode = NULL;
  }
  // cout << "extended phase " << i << s[i] << endl;
  // printState();
}

int main() {
  int t;
  cin >> t;
  string s;
  vector<string> o;
  for (int ct = 0; ct < t; ct++) {
    init();
    cin >> s;
    for (auto c: s) {
      extend(c);
    }
    o.clear();
    for (auto node: nodes) {
      for (auto p: node->edgeMap) {
        string co = "";
        for (int i = p.second->start; i < min((int) s.size(), p.second->start + p.second->length); i++) co += s[i];
        o.push_back(co);
      }
    }
    sort(o.begin(), o.end());
    cout << 1 + ct << endl;
    for (auto co: o) {
      cout << co << endl;
    }
  }
  return 0;
}
