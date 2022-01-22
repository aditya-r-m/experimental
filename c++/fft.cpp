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

vector<complex<double>> fft(vector<complex<double>> &input, complex<double> w) {
    if (input.size() == 1) return input;
    if (input.size() & 1) throw invalid_argument("Input size should be a power of 2");

    vector<complex<double>> result;

    vector<complex<double>> inputE, inputO;
    for (int i = 0; i < input.size(); i++) {
        if (i & 1) inputO.push_back(input[i]);
        else inputE.push_back(input[i]);
    }
    vector<complex<double>> resultE = fft(inputE, w*w);
    vector<complex<double>> resultO = fft(inputO, w*w);

    int i;
    complex<double> iw;
    for (i = 0, iw = 1. + 0i; i < resultE.size(); i++, iw *= w) {
        result.push_back(resultE[i] + iw*resultO[i]);
    }
    for (i = 0, iw = 1. + 0i; i < resultE.size(); i++, iw *= w) {
        result.push_back(resultE[i] - iw*resultO[i]);
    }
    return result;
}

int main() {
    int l = 8;
    complex<double> w = exp(complex<double>(0, 1) * (2 * M_PI / l));
    vector<complex<double>> v(l);
    v[1] = 1;
    vector<complex<double>> f = fft(v, w);
    for (auto fe : f) cout << round(fe) << " ";
    cout << endl;
    for (auto ve : fft(f, conj(w))) cout << round(ve) << " ";
    cout << endl;
    return 0;
}

