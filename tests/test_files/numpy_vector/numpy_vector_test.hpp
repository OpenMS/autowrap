#pragma once
#include <vector>

class NumpyVectorTest
{
public:
    NumpyVectorTest() {}
    
    // Test simple vector output (const ref - should copy)
    const std::vector<double>& getConstRefVector() {
        static std::vector<double> data = {1.0, 2.0, 3.0, 4.0, 5.0};
        return data;
    }
    
    // Test simple vector output (non-const ref - should be view)
    std::vector<double>& getMutableRefVector() {
        static std::vector<double> data = {10.0, 20.0, 30.0};
        return data;
    }
    
    // Test simple vector output (value - should copy)
    std::vector<double> getValueVector(size_t size) {
        std::vector<double> result;
        for (size_t i = 0; i < size; i++) {
            result.push_back(static_cast<double>(i) * 2.0);
        }
        return result;
    }
    
    // Test simple vector input
    double sumVector(const std::vector<double>& data) {
        double sum = 0.0;
        for (double val : data) {
            sum += val;
        }
        return sum;
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
