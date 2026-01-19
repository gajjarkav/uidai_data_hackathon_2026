# ============================================================
# 🔧 MULTI-DATASET RECENCY FIX FOR ASIS SCORE
# ============================================================
# 
# This file contains the corrected code for Sections 4.1, 4.2, and 4.3
# of the hackathon_winning_solutions.ipynb notebook.
# 
# PROBLEM: The original recency calculation ONLY uses enrollment dates,
# ignoring demographic and biometric update dates. This means districts
# with old enrollments but recent updates will incorrectly show LOW recency.
#
# SOLUTION: Calculate recency using the LATEST date across ALL three datasets
# (enrollment, demographic, biometric) to capture true service activity.
#
# Copy and paste these code sections into the respective cells in the notebook.
# ============================================================


# ============================================================
# SECTION 4.1 - REPLACE THE ENTIRE CELL WITH THIS CODE:
# ============================================================

"""
# 4.1 Aggregate metrics by State and District
print('📊 Computing ASIS Score Components...')
print('='*60)

# Enrollment Aggregates - 🔧 FIXED: Renamed to latest_enrollment_date
enrollment_agg = enrollment_df.groupby(['state', 'district']).agg(
    total_enrollments=('pincode', 'count'),
    unique_pincodes=('pincode', 'nunique'),
    age_0_5_sum=('age_0_5', 'sum'),
    age_5_17_sum=('age_5_17', 'sum'),
    age_18_plus_sum=('age_18_greater', 'sum'),
    latest_enrollment_date=('date', 'max')  # 🔧 FIXED: Renamed for clarity
).reset_index()

enrollment_agg['youth_enrollment'] = enrollment_agg['age_0_5_sum'] + enrollment_agg['age_5_17_sum']
print(f'✅ Enrollment aggregates: {len(enrollment_agg)} district records')

# Demographic Update Aggregates - 🔧 FIXED: Now includes latest_demo_date
demographic_agg = demographic_df.groupby(['state', 'district']).agg(
    demo_updates=('pincode', 'count'),
    demo_youth=('demo_age_5_17', 'sum'),
    demo_adult=('demo_age_17_greater', 'sum'),
    latest_demo_date=('date', 'max')  # 🔧 ADDED: Track latest demographic update date
).reset_index()
print(f'✅ Demographic aggregates: {len(demographic_agg)} district records')

# Biometric Update Aggregates - 🔧 FIXED: Now includes latest_bio_date
biometric_agg = biometric_df.groupby(['state', 'district']).agg(
    bio_updates=('pincode', 'count'),
    bio_youth=('bio_age_5_17', 'sum'),
    bio_adult=('bio_age_17_', 'sum'),
    latest_bio_date=('date', 'max')  # 🔧 ADDED: Track latest biometric update date
).reset_index()
print(f'✅ Biometric aggregates: {len(biometric_agg)} district records')
"""


# ============================================================
# SECTION 4.2 - REPLACE THE ENTIRE CELL WITH THIS CODE:
# ============================================================

"""
# 4.2 Merge all aggregates into unified district profile
print('\\n🔗 Merging datasets into Unified District Profile...')

# Merge enrollment with demographic
unified = pd.merge(enrollment_agg, demographic_agg, on=['state', 'district'], how='outer')

# Merge with biometric
unified = pd.merge(unified, biometric_agg, on=['state', 'district'], how='outer')

# 🔧 FIXED: Handle date columns separately before fillna(0)
# Store date columns before filling
date_columns = ['latest_enrollment_date', 'latest_demo_date', 'latest_bio_date']
date_data = unified[date_columns].copy()

# Fill missing numeric values with 0
numeric_cols = [col for col in unified.columns if col not in date_columns + ['state', 'district']]
unified[numeric_cols] = unified[numeric_cols].fillna(0)

# Restore date columns (NaT will be handled in recency calculation)
unified[date_columns] = date_data

print(f'✅ Unified Profile: {len(unified)} districts with cross-dataset metrics')
print(f'   Columns: {list(unified.columns)}')
"""


# ============================================================
# SECTION 4.3 - REPLACE THE ENTIRE CELL WITH THIS CODE:
# ============================================================

"""
# 4.3 Calculate ASIS Score Components
print('\\n📐 Calculating ASIS Score Components...')

# Component 1: Enrollment Density (normalize per state)
state_avg = unified.groupby('state')['total_enrollments'].transform('mean')
unified['enrollment_density_raw'] = unified['total_enrollments'] / (state_avg + 1)

# Component 2: Update Compliance Rate
unified['total_updates'] = unified['demo_updates'] + unified['bio_updates']
unified['update_compliance_raw'] = unified['total_updates'] / (unified['total_enrollments'] + 1)

# Component 3: Youth Coverage Index
unified['total_youth'] = unified['youth_enrollment'] + unified['demo_youth'] + unified['bio_youth']
unified['total_all'] = (unified['total_enrollments'] + unified['demo_updates'] + unified['bio_updates'])
unified['youth_coverage_raw'] = unified['total_youth'] / (unified['total_all'] + 1)

# ============================================================
# 🔧 FIXED: Component 4 - Multi-Dataset Service Recency
# ============================================================
# OLD CODE (only used enrollment dates):
#   max_date = enrollment_df['date'].max()
#   unified['days_since_last'] = (max_date - pd.to_datetime(unified['latest_date'])).dt.days.fillna(365)
#
# NEW CODE: Uses LATEST date across ALL three datasets (enrollment, demographic, biometric)
# This catches districts with low enrollments but high update activity!

# 🎯 NEW RECENCY CALCULATION - Use LATEST date across ALL datasets
unified['latest_date_any'] = unified[['latest_enrollment_date', 'latest_demo_date', 'latest_bio_date']].max(axis=1)

# Calculate the global maximum date across ALL datasets
max_date = pd.to_datetime([
    enrollment_df['date'].max(),
    demographic_df['date'].max(),
    biometric_df['date'].max()
]).max()

# Calculate recency using the MOST RECENT activity across all datasets
unified['days_since_last'] = (max_date - pd.to_datetime(unified['latest_date_any'])).dt.days.fillna(365)
unified['recency_raw'] = 1 - (unified['days_since_last'] / 365).clip(0, 1)

print('✅ All component scores calculated')
print(f'   📍 Note: Recency now uses multi-dataset fusion (enrollment + demographic + biometric)')
"""


# ============================================================
# WHY THIS FIX MATTERS - For Your Hackathon Presentation
# ============================================================
#
# BEFORE (Single-Dataset Recency):
# - District X: Last enrollment 60 days ago, Last biometric update 2 days ago
# - Recency Score: LOW (based only on 60-day old enrollment)
# - PROBLEM: Misses the fact that district is highly active!
#
# AFTER (Multi-Dataset Recency):
# - District X: Last enrollment 60 days ago, Last biometric update 2 days ago
# - Recency Score: HIGH (based on 2-day old biometric update)
# - CORRECT: Captures true service activity across all touchpoints!
#
# Tell the judges:
# "We initially calculated recency from enrollment data alone, but realized 
# this missed active districts doing lots of updates. So we engineered a 
# MULTI-DATASET RECENCY SCORE that looks at the LATEST activity across all 
# three datasets. This catches districts with low enrollments but high update 
# activity - a pattern invisible to single-dataset analysis."
#
# This demonstrates:
# 1. ✅ Critical thinking (you found and fixed a flaw)
# 2. ✅ Data fusion expertise (you combined datasets smartly)
# 3. ✅ Real-world understanding (updates matter as much as enrollments)
# ============================================================
