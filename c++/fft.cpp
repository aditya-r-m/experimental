#include<iostream>
#include<complex>
#include<vector>
#include<cmath>

using namespace std;

double round(double d) {
    return (int)(d*1000.0 + 0.5 - (d<0)) / 1000.0;
}

complex<double> round(complex<double> c) {
    return complex<double>(round(real(c)), round(imag(c)));
}

vector<complex<double>> fft(vector<complex<double>> &input, bool inverse) {
    if (input.size() == 1) return input;
    if (input.size() & 1) throw invalid_argument("Input size should be a power of 2");

    vector<complex<double>> result;

    vector<complex<double>> inputE, inputO;
    for (int i = 0; i < input.size(); i++) {
        if (i & 1) inputO.push_back(input[i]);
        else inputE.push_back(input[i]);
    }
    vector<complex<double>> resultE = fft(inputE, inverse);
    vector<complex<double>> resultO = fft(inputO, inverse);

    int i;
    complex<double> w, wb = exp(complex<double>(0, inverse ? -1 : 1) * (2 * M_PI / input.size()));
    for (i = 0, w = 1. + 0i; i < resultE.size(); i++, w *= wb) {
        result.push_back(resultE[i] + w*resultO[i]);
    }
    for (i = 0, w = 1. + 0i; i < resultE.size(); i++, w *= wb) {
        result.push_back(resultE[i] - w*resultO[i]);
    }
    return result;
}

int main() {
    int l = 8;
    vector<complex<double>> v(l);
    v[1] = 1;
    vector<complex<double>> f = fft(v, false);
    for (auto x : f) cout << round(x) << " ";
    cout << endl;
    for (auto v : fft(f, true)) cout << round(v) << " ";
    cout << endl;
    return 0;
}

