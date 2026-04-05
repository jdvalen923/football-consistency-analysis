# Player Performance Consistency Analysis

This repository contains the code used for my Bachelor Thesis:

**"Beyond Averages: A Coefficient of Variation Approach to Player Performance Consistency in Professional Football"**

---

## Overview

This project analyses match-to-match performance consistency of professional football players in the 2024/25 LaLiga season.

The study focuses on:
- Measuring consistency using the coefficient of variation (CV)
- Evaluating the role of positional differences
- Assessing the impact of opponent difficulty
- Testing the relationship between performance level and consistency (expertise hypothesis)

---

## Repository Structure

- `data/` → Contains the final dataset used in the analysis and a sample of raw data  
- `scripts/` → Full data processing and modelling pipeline  
- `figures/` → Visual outputs used in the thesis  
- `regression_models/` → Model outputs and regression results  

---

## Methodology

The analysis follows a structured pipeline:

1. Data extraction from the Sofascore API  
2. Data preprocessing and filtering  
3. Computation of consistency metrics (CV and SD)  
4. Exploratory data analysis and visualisation  
5. Regression modelling (OLS)  

---

## Reproducibility

The repository includes all scripts required to replicate the analysis and results presented in the thesis.

Raw match-level data files are not fully included due to size constraints, but can be reconstructed using the data extraction scripts provided.

---

## Author

Valentín Miguel Uriarte  
Dual Degree in Business Administration & Data and Business Analytics  
IE University
