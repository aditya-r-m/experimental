#include <iostream>
#include <limits>
#include <map>
#include <math.h>
#include <string>
#include <vector>

using namespace std;

namespace ukkonen {

static const int INF = std::numeric_limits<int>::max();

vector<char> text;

struct Node;
struct Edge {
  int start, length;
  Node *source, *dest;

  Edge(int s, int l, Node *src, Node *dst)
      : start{s}, length{l}, source{src}, dest{dst} {}
};

int nxtNodeId;
struct Node {
  int id;
  map<char, Edge *> edges;
  Node *suffixLink;

  Node() : id{nxtNodeId++} { suffixLink = NULL; }

  void print(string prefix) {
    cout << prefix << "node " << id;
    if (suffixLink != NULL)
      cout << endl << prefix << "suffix link: " << suffixLink->id;
    for (auto edgePair : edges) {
      Edge *edge = edgePair.second;
      cout << endl << endl;
      cout << prefix << "node " << id << endl;
      cout << prefix << "edge " << edge->start << "-" << edge->length << "  ";
      for (int i = edge->start;
           i < (edge->length == INF ? text.size() : edge->start + edge->length);
           i++) {
        cout << text[i];
      }
      cout << endl;
      edgePair.second->dest->print(prefix + " ");
    }
  }
} * root;

int remainder;
Node *activeNode;
Edge *activeEdge;
int activeLength;
Node *lastAddedInternalNode;

void print() {
  cout << "remainder " << remainder << endl;
  cout << "active node " << activeNode->id << endl;
  if (activeEdge != NULL)
    cout << "active edge " << activeEdge->source->id << "->"
         << activeEdge->dest->id << endl;
  cout << "active length " << activeLength << endl;
  if (lastAddedInternalNode != NULL)
    cout << "last added internal node " << lastAddedInternalNode->id << endl
         << endl;
  root->print("");
  cout << endl << "--------------------" << endl << endl;
}

void init() {
  text.clear();
  nxtNodeId = 0;
  root = new Node();
  remainder = 0;
  activeNode = root;
  activeEdge = NULL;
  activeLength = 0;
  lastAddedInternalNode = NULL;
}

void extend(char c) {
  text.push_back(c);

  if (!remainder)
    remainder++;

  cout << endl
       << "====================" << endl
       << endl
       << "extending " << c << " " << text.size() - 1 << " rem " << remainder
       << endl
       << endl;
  print();

  bool done = false;
  while (!done) {

    if (activeEdge == NULL) {

      if (activeNode->edges.count(c)) {
        remainder++;
        activeEdge = activeNode->edges[c];
        activeLength++;
        if (activeLength == activeEdge->length) {
          activeNode = activeEdge->dest;
          activeEdge = NULL;
          activeLength = 0;
        }
        done = true;
      } else {
        remainder--;
        Node *nLeaf = new Node();
        activeNode->edges[c] =
            new Edge(text.size() - 1, INF, activeNode, nLeaf);
        if (!remainder)
          done = true;
        else
          activeNode = activeNode->suffixLink;
      }

    } else {

      if (text[activeEdge->start + activeLength] == c) {
        remainder++;
        activeLength++;
        if (activeLength == activeEdge->length) {
          activeNode = activeEdge->dest;
          activeEdge = NULL;
          activeLength = 0;
        }
        done = true;
      } else {
        remainder--;
        Node *nInternal = new Node();
        Edge *nInternalToODest = new Edge(
            activeEdge->start + activeLength,
            activeEdge->length == INF ? INF : activeEdge->length - activeLength,
            nInternal, activeEdge->dest);
        nInternal->edges[text[activeEdge->start + activeLength]] =
            nInternalToODest;
        Node *nLeaf = new Node();
        Edge *nInternalToNLeaf =
            new Edge(text.size() - 1, INF, nInternal, nLeaf);
        nInternal->edges[c] = nInternalToNLeaf;
        activeEdge->length = activeLength;
        activeEdge->dest = nInternal;
        if (lastAddedInternalNode != NULL)
          lastAddedInternalNode->suffixLink = nInternal;
        lastAddedInternalNode = nInternal;

        int activeStart = activeEdge->start;
        if (activeNode != root)
          activeNode = activeNode->suffixLink;
        else {
          activeLength--;
          activeStart++;
        }
        activeEdge = activeNode->edges[text[activeStart]];
        while (activeLength >= activeEdge->length) {
          activeNode = activeEdge->dest;
          activeLength -= activeEdge->length;
          activeStart += activeEdge->length;
          if (!activeLength) break;
          activeEdge = activeNode->edges[text[activeStart]];
        }
        if (!activeLength) {
          activeEdge = NULL;
          if (lastAddedInternalNode != NULL) {
            lastAddedInternalNode->suffixLink = activeNode;
            lastAddedInternalNode = NULL;
          }
        }
      }

    }
    print();
  }
}

bool match(string p, Node *n = root, int i = 0) {
  if (i == p.length())
    return true;
  if (!n->edges.count(p[i]))
    return false;
  auto e = n->edges[p[i]];
  for (int j = e->start;
       j < (e->length == INF ? 1 + text.size() : e->start + e->length);
       j++, i++) {
    if (i == p.length())
      return true;
    if (j == text.size())
      return false;
    if (text[j] != p[i])
      return false;
  }
  return match(p, e->dest, i);
}

} // namespace ukkonen

int main() {
  ukkonen::init();
  string txt = "aabaacaad";
  // string txt = "abcabdabce";
  // string txt = "abcdacdacde";
  for (auto c : txt)
    ukkonen::extend(c);
  ukkonen::print();
  auto ps = {"ab", "ac", "ad", "ae"};
  for (auto p : ps) {
    cout << p << " " << ukkonen::match(p) << endl;
  }
  return 0;
}
