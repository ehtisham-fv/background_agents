# Master Data Comparison Report

## Executive Summary

This report presents a comprehensive analysis comparing the consolidated purchase prices from our recent price analysis with the master product data from our pricing system. The analysis reveals significant price discrepancies that require immediate attention.

## Key Findings

### 📊 **Data Coverage**
- **Total Articles in Consolidated Data**: 25,155
- **Total Articles in Master Data**: 293,305
- **Common Articles Found**: 24,537 (97.5% coverage)
- **Missing from Master Data**: 618 articles (2.5%)

### 💰 **Price Discrepancy Analysis**
- **Articles with Price Differences**: 18,212 out of 24,537 (74.2%)
- **Average Price Difference**: €-8.56 (consolidated prices are lower on average)
- **Median Price Difference**: €-5.76
- **Largest Price Increase**: €39.31 (Article 20587)
- **Largest Price Decrease**: €-91.16 (Article 1604427)

## Detailed Analysis

### 1. **Missing Articles**
618 articles from our consolidated purchase price list are not found in the master product data. This represents a 2.5% gap that needs to be addressed. These missing articles include:
- 1554785, 1555634, 1590122, 1620711, 1621337, and 613 others
- Complete list available in: `missing_articles_in_master.csv`

### 2. **Price Discrepancies**

#### **Significant Price Increases (Consolidated > Master)**
The top 10 articles with the largest price increases show concerning patterns:
- **Article 20587**: €0.00 → €39.31 (+€39.31)
- **Article 22134**: €19.00 → €56.00 (+€37.00, +194.7%)
- **Multiple articles (21076-21082)**: €49.23 → €84.00 (+€34.77, +70.6%)

#### **Significant Price Decreases (Consolidated < Master)**
The top 10 articles with the largest price decreases indicate potential cost savings:
- **Article 1604427**: €281.15 → €189.99 (-€91.16, -32.4%)
- **Article 1675601**: €169.10 → €89.25 (-€79.85, -47.2%)
- **Article 1478621**: €161.41 → €85.05 (-€76.36, -47.3%)

### 3. **Statistical Distribution**
- **74.2%** of articles have price discrepancies
- **Standard Deviation**: €11.87 (indicating high variability)
- **Price Range**: From -€91.16 to +€39.31

## Business Impact

### **Immediate Actions Required**

1. **Data Synchronization**: Investigate why 618 articles are missing from the master data
2. **Price Validation**: Review the 18,212 articles with price discrepancies
3. **Cost Optimization**: Leverage the identified price decreases for potential savings
4. **System Integration**: Ensure regular synchronization between systems

### **Financial Implications**

- **Potential Savings**: Articles showing lower consolidated prices could result in significant cost reductions
- **Risk Exposure**: Articles with higher consolidated prices may indicate increased procurement costs
- **Data Quality**: 74.2% discrepancy rate suggests systematic issues requiring attention

## Recommendations

### **Short-term (1-4 weeks)**
1. **Audit Missing Articles**: Investigate the 618 missing articles and add them to the master data
2. **Validate Top Discrepancies**: Manually review the top 50 articles with largest price differences
3. **Update Master Prices**: Consider updating master data with more recent consolidated prices where appropriate

### **Medium-term (1-3 months)**
1. **Automated Synchronization**: Implement automated data sync between systems
2. **Price Monitoring**: Set up alerts for significant price changes
3. **Regular Reconciliation**: Establish monthly comparison processes

### **Long-term (3-12 months)**
1. **System Integration**: Integrate pricing systems to ensure real-time consistency
2. **Data Governance**: Establish clear data ownership and update procedures
3. **Analytics Dashboard**: Create real-time monitoring dashboards for price consistency

## Supporting Files

This analysis has generated the following supporting files:

1. **`price_comparison_results.csv`** - Complete comparison of all 24,537 common articles
2. **`price_discrepancies_only.csv`** - Only the 18,212 articles with price differences
3. **`missing_articles_in_master.csv`** - List of 618 missing articles
4. **`plots/price_comparison_overview.png`** - Visual overview of price distributions
5. **`plots/top_discrepancies.png`** - Charts showing top price increases and decreases

## Technical Notes

- **Article Number Extraction**: Successfully extracted article numbers from Product ID format (CategoryName_ArticleNumber)
- **Data Quality**: Both datasets were cleaned and standardized before comparison
- **Matching Logic**: 97.5% match rate demonstrates high data quality overall
- **Analysis Scope**: Focused only on articles present in consolidated data as requested

## Conclusion

While the 97.5% coverage rate is excellent, the 74.2% price discrepancy rate indicates significant systematic issues that require immediate attention. The analysis provides clear direction for both cost optimization opportunities and data quality improvements.

**Priority**: HIGH - Immediate action required for data synchronization and price validation.

---
*Report generated on: 2025-09-09*  
*Analysis covers: 25,155 consolidated articles vs 293,305 master data articles*
