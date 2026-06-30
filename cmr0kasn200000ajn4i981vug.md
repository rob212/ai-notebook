---
title: "AI Model Risk Categories"
datePublished: 2026-06-30T11:27:09.195Z
cuid: cmr0kasn200000ajn4i981vug
slug: ai-model-risk-categories
tags: ai-governance, ai-risk, model-risk-management

---

Managing AI Model risk isn't optional; it's critical governance.

Let's discuss how to manage model risk before it becomes a news headline about your company. In this post we will cover how to:

1.  Recognise the major categories of model risk.
    
2.  Map each category to the proper governance control.
    
3.  Choose KPIs that make risk visible and measurable.
    

Model risk *typically* manifests in 4 forms:

1.  **Data and Concept Drift**:
    
    1.  When **input distributions shift** or the **relationship between variables change**.
        
    2.  Change in data can be **gradual** or **sudden -** either way it is a change in the underlying data or reality of the world that the model must adapt to
        
2.  **Bias and Fairness Risk:**
    
    1.  When errors effect some groups more than others.
        
3.  **Performance Degradation:**
    
    1.  When **accuracy** or **stability** drops over time. This may be indicative of data/concept drift, data processing pipeline failures (i.e. data has not been refreshed). Or part of a flawed model construction that becomes obvious over time.
        
4.  **Misuse and Operational Risk:**
    
    1.  When a model is used outside its intended purpose or changes are made outside review.
        

Each of these risks can be managed with proper control. For drift you can setup monitoring jobs or retraining triggers. For bias, fairness audits and pre-deployment checks are key. For performance, we add regular back testing and stability reviews. For operational risk, you will want to have strong access controls, documented change approvals and audit trails.

### Measuring Controls

The controls only matter if we measure them.

**Drift** - Track metrics such as population stability index.

**Performance** - Look at AUC stability (Area Under the Receiver Operating Characteristic Curve) or calibration error.

**Fairness -** Monitor the disparity between groups.

**Operations** - Track override rates, open incidents and SLA adherence (Service Level Agreement).

## Micro Case Studies

Let's say we are working for a bank that has deployed AI models into it's loan approval systems globally. In production an issue is identified that without any code changes on recent deployments, loan approvals spike in an particular east region.

**Issue**: Approval spike in east region

**Risk**: data/concept drift

**Controls:** Retraining triggers and approval gates

**KPIs:** PSI (Population Stability Index) on income and region, weekly AUC stability, fairness gap across demographic groups

This quick mapping turns an abstract risk into a more concrete actionable plan.

Let's think of another case study you might observe...

You may discover that a fairness gap has doubled for Group A, compared to Group B, but performance has remained stable overall. You should therefore conduct fairness audits with demographic parity measures. It's not drift, not latency but fairness that is the core issue here.

### Summary

Don't just name risks, map them to controls and KPIs to make them visible, measurable and governable.