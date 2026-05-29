"""Centralized CSS selectors for Recap viewer UI elements."""

# Project browser panel
PROJECT_BROWSER_TITLE = '.docking-panel-title:has-text("Project Browser")'
PROJECT_BROWSER_TOGGLE = "#recap-pcv-project-panel, #recap-rv-project-panel"
PROJECT_BROWSER_SEARCH = "#search-input"
PROJECT_BROWSER_NO_RESULTS = "#project-panel-search-container .no-result-item"

# Scans tab
SCANS_TAB_PAGE = "#tab-page-scan"
SCANS_ROOT = "#Root"
SCANS_TREE_ITEM = "#tab-page-scan > .tree-node span.line-item-text"
SCANS_CHILD_ITEMS = "#tab-page-scan > .tree-node:not(#Root) span.line-item-text"
SCAN_GROUP_LABEL = "#Root span.line-item-text"

# Annotations tab
ANNOTATIONS_TAB_HEADER = "#tab-header-annotation"
ANNOTATIONS_TAB_PAGE = "#tab-page-annotation"
ANNOTATION_ITEMS = "#tab-page-annotation .line-item .line-item-text"

# View States tab
VIEW_STATES_TAB_HEADER = "#tab-header-view-state"
VIEW_STATES_TAB_PAGE = "#tab-page-view-state"
VIEW_STATES_GROUP = "#Root-ViewState span.line-item-text"
VIEW_STATE_ITEMS = (
    "#tab-page-view-state > .tree-node:not(#Root-ViewState) span.line-item-text"
)

# Extracted Features tab
EXTRACTED_FEATURES_TAB_HEADER = "#tab-header-linear-feature"
EXTRACTED_FEATURES_TAB_PAGE = "#tab-page-linear-feature"
EXTRACTED_FEATURES_GROUP = "#point-first-level > .lf-tree-item-container"
EXTRACTED_FEATURES_CHILDREN = (
    "#tab-page-linear-feature #point-first-level > .lf-tree-node-children-container"
)
EXTRACTED_FEATURE_INPUTS = (
    "#tab-page-linear-feature #point-first-level > .lf-tree-node-children-container "
    "> .lf-tree-node-container input.lf-curb-name-container[id$='-lf-title']"
)
EXTRACTED_FEATURE_INPUTS_TEMPLATE = (
    "{tab_page} #point-first-level > .lf-tree-node-children-container "
    "> .lf-tree-node-container input.lf-curb-name-container[id$='-lf-title']"
)

# Generic tree item selectors used during search verification
TREE_TEXT_ITEMS = "{tab_page} span.line-item-text, {tab_page} .line-item-text"

# Bottom toolbar – scan group workflow
BOTTOM_SCAN_GROUP = "#recap-pcv-scan-group"
BOTTOM_SCAN_GROUP_DONE = "#recap-pcv-scan-group-done"
SCAN_GROUP_MODAL_OVERLAY = '[data-testid="modal-overlay"]'
SCAN_GROUP_TUTORIAL_NEXT_CLASS = "button.recap-scan-group-step1"
SCAN_GROUP_TUTORIAL_OK_CLASS = "button.recap-scan-group-step2"
