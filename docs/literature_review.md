# Literature Review: Predictive Cyber Attack Detection

| Research Paper Title | Variables & Features Used | Variables & Features in Our Dataset | Difference between Research Dataset & Our Dataset | Remarks |
|----------------------|---------------------------|-------------------------------------|---------------------------------------------------|---------|
| **Toward Generating a New Intrusion Detection Dataset and Intrusion Traffic Characterization (CIC-IDS 2017 Original Paper)** | 80 basic flow features (Duration, Pkt Size, IAT, Flags) | All 80 CICFlowMeter features | Same dataset (Primary Source) | Baseline paper. We should use this to benchmark our cleaning process. |
| **A comprehensive evaluation of Network Intrusion Detection Systems using UNSW-NB15 dataset** | 49 features (srcip, dstip, proto, state, dur, sbytes, dbytes, etc.) | 80 CICFlowMeter features | UNSW-NB15 has strictly defined train/test sets; CIC-IDS is daily capture. | UNSW-NB15 features are more packet-header focused; Our dataset is flow-statistical. |
| **Survey on Deep Learning for NIDS** (Example Title) | Raw packet bytes, Flow images | Statistical Flow Features (CSV) | Many DL papers use payload data; we use metadata only. | Flow features are lighter and better for privacy than payload inspection. |
| **Machine Learning for DDoS Detection in SDN** | Packet-In rate, Flow entry count | Flow Duration, Packet/s, Byte/s | Synthetic SDN traces vs Real University Network traffic. | Our real-world data is noisier but more valid for academic assessment. |
| **NIDS using Random Forest and SMOTE** | Basic 5-tuple + Packet Count | Full 80+ features including IAT and Window size | KDD99 (Outdated) vs CIC-IDS 2017 | KDD99 is obsolete. Our choice of CIC-IDS is superior for modern attacks. |
| **An Explainable Machine Learning Framework for Intrusion Detection** | Top 20 Feature Selection (PCA) | Full feature set -> Selected Top K | NSL-KDD vs CIC-IDS 2017 | We must implement Feature Importance plots (Random Forest) for explainability. |
| **Time-Series Anomaly Detection in Network Traffic** | Traffic Volume (Bytes/sec) over time | Aggregated Window Features (Entropy, Rates) | ISP backbone logs vs Campus flow logs | Pure time-series ignores behavioral flags; our hybrid approach is better. |
| **Botnet Detection using Flow Intervals** | Flow IAT (Inter-Arrival Time) statistics | Flow IAT Mean, Std, Max, Min | Bot-IoT Dataset vs CIC-IDS 2017 | CIC-IDS contains Botnet traffic (Ares), good for validation. |
| **XGBoost for High Speed Network Traffic Analysis** | Header length, Flag counts | Flag counts (FIN, SYN, RST, PSH, ACK) | Private ISP Data vs Public CIC-IDS | XGBoost is proven effective; a mandatory model for our comparison. |
| **Intrusion Detection System using LSTM** | Sequence of packet sizes | Sequence of Time-Windows | DARPA 1998 (Ancient) vs CIC-IDS 2017 | LSTM justifies our "Predictive" claim by looking at history $t-1, \dots, t-k$. |
| **Feature Selection for IDS using genetic algorithms** | Optimized subset of 12 features | We will use Feature Importance (RF) | KDDCup99 | Genetic algorithms are slow; Tree-based selection is preferred for our timeline. |
| **Real-time DDoS detection using Decision Trees** | Packet Rate, Entropy of SrcIP | Pkt/s, Flow/s, Entropy (Computed) | CAIDA DDoS 2007 | We need to implement 'Entropy' manually as a custom feature in aggregation. |
| **Comparison of ML classifiers for Network Security** | Naive Bayes, SVM, KNN | LR, RF, XGB, LSTM | NSL-KDD | SVM and KNN are too slow for large flow datasets (2M+ rows); we stick to Trees/NN. |
| **Network Traffic Forecasting using ARIMA** | Total Bandwidth usage | Attack Probability (0/1) | General Internet Traffic | Forecasting *bandwidth* is widely done; forecasting *attacks* is our novel angle. |
| **Evaluation of IDS datasets** | Meta-analysis of feature sets | N/A | Compare KDD, UNSW, CIC | Confirms CIC-IDS 2017 is the most balanced modern dataset for supervision. |

## Summary of Findings
- **Gap Identified**: Most papers focus on *classifying the current packet/flow* (Detection).
- **Our Contribution**: We focus on *predicting the future state* (Prediction) by aggregating flows into time windows.
- **Dataset Choice**: CIC-IDS 2017 is the consensus "modern standard" replacing KDD99.
