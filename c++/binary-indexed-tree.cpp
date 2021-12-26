#include<iostream>
#include<vector>

using namespace std;

struct BinaryIndexedTree {
    vector<int> v;

    BinaryIndexedTree(int sz) {
        v.resize(sz);
    }

    void add(int i, int d) {
        if (i == 0) {
            v[0] = d;
            return;
        }
        for (; i < v.size(); i += i&-i) v[i] += d;
    }

    int query(int i) {
        int s = v[0];
        for (; i > 0; i &= i-1 /* i -= i&-i */) s += v[i];
        return s;
    }
};

int main() {
    int l = 10;
    BinaryIndexedTree tree(l);
    for (int i = 0; i < l; i++) tree.add(i, i);
    for (int i = 0; i < l; i++) cout << tree.query(i) << "\t";
    cout << endl;
    return 0;
}

