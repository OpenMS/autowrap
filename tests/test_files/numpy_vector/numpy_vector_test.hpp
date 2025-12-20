#pragma once
#include <vector>

class NumpyVectorTest
{
public:
    NumpyVectorTest() {}
    
    // Test simple vector input
    double sumVector(const std::vector<double>& data) {
        double sum = 0.0;
        for (double val : data) {
            sum += val;
        }
        return sum;
    }
    
    // Test simple vector output
    std::vector<double> createVector(size_t size) {
        std::vector<double> result;
        for (size_t i = 0; i < size; i++) {
            result.push_back(static_cast<double>(i) * 2.0);
        }
        return result;
    }
    
    // Test simple vector input/output (modify in place via reference)
    void multiplyVector(std::vector<double>& data, double factor) {
        for (size_t i = 0; i < data.size(); i++) {
            data[i] *= factor;
        }
    }
    
    // Test different numeric types
    int sumIntVector(const std::vector<int>& data) {
        int sum = 0;
        for (int val : data) {
            sum += val;
        }
        return sum;
    }
    
    std::vector<float> createFloatVector(size_t size) {
        std::vector<float> result;
        for (size_t i = 0; i < size; i++) {
            result.push_back(static_cast<float>(i) + 0.5f);
        }
        return result;
    }
    
    // Test nested vectors (2D arrays)
    std::vector<std::vector<double>> create2DVector(size_t rows, size_t cols) {
        std::vector<std::vector<double>> result;
        for (size_t i = 0; i < rows; i++) {
            std::vector<double> row;
            for (size_t j = 0; j < cols; j++) {
                row.push_back(static_cast<double>(i * cols + j));
            }
            result.push_back(row);
        }
        return result;
    }
    
    double sum2DVector(const std::vector<std::vector<double>>& data) {
        double sum = 0.0;
        for (const auto& row : data) {
            for (double val : row) {
                sum += val;
            }
        }
        return sum;
    }
};
