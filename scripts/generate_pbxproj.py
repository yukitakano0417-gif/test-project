#!/usr/bin/env python3
"""Generates TodoNotes.xcodeproj/project.pbxproj from scratch.

This is a one-off generator (no Xcode available in this environment to
produce the project file the normal way). Run with: python3 scripts/generate_pbxproj.py
"""
import secrets

def uid():
    return secrets.token_hex(12).upper()

# ---- allocate ids -----------------------------------------------------
ids = {}
def new_id(name):
    i = uid()
    ids[name] = i
    return i

# Swift sources
swift_files = [
    ("TodoNotesApp.swift", None),
    ("TodoItem.swift", "Models"),
    ("NoteColor.swift", "Models"),
    ("TodoNote.swift", "Models"),
    ("NoteStore.swift", "Store"),
    ("Haptics.swift", "Store"),
    ("ContentView.swift", "Views"),
    ("NoteCardView.swift", "Views"),
    ("ColorPickerRow.swift", "Views"),
    ("NoteEditorView.swift", "Views"),
]

for fname, _ in swift_files:
    new_id(f"fileref_{fname}")
    new_id(f"buildfile_{fname}")

new_id("fileref_Assets.xcassets")
new_id("buildfile_Assets.xcassets")
new_id("fileref_PrivacyInfo.xcprivacy")
new_id("buildfile_PrivacyInfo.xcprivacy")
new_id("fileref_PreviewAssets.xcassets")
new_id("fileref_product")

new_id("group_main")
new_id("group_TodoNotes")
new_id("group_Models")
new_id("group_Store")
new_id("group_Views")
new_id("group_PreviewContent")
new_id("group_Products")

new_id("phase_sources")
new_id("phase_frameworks")
new_id("phase_resources")

new_id("target")
new_id("project")

new_id("config_project_debug")
new_id("config_project_release")
new_id("config_target_debug")
new_id("config_target_release")
new_id("configlist_project")
new_id("configlist_target")

# ---- PBXBuildFile -------------------------------------------------------
buildfile_lines = []
for fname, _ in swift_files:
    buildfile_lines.append(
        f'\t\t{ids[f"buildfile_{fname}"]} /* {fname} in Sources */ = '
        f'{{isa = PBXBuildFile; fileRef = {ids[f"fileref_{fname}"]} /* {fname} */; }};'
    )
buildfile_lines.append(
    f'\t\t{ids["buildfile_Assets.xcassets"]} /* Assets.xcassets in Resources */ = '
    f'{{isa = PBXBuildFile; fileRef = {ids["fileref_Assets.xcassets"]} /* Assets.xcassets */; }};'
)
buildfile_lines.append(
    f'\t\t{ids["buildfile_PrivacyInfo.xcprivacy"]} /* PrivacyInfo.xcprivacy in Resources */ = '
    f'{{isa = PBXBuildFile; fileRef = {ids["fileref_PrivacyInfo.xcprivacy"]} /* PrivacyInfo.xcprivacy */; }};'
)

# ---- PBXFileReference ----------------------------------------------------
fileref_lines = []
for fname, _ in swift_files:
    fileref_lines.append(
        f'\t\t{ids[f"fileref_{fname}"]} /* {fname} */ = '
        f'{{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = {fname}; sourceTree = "<group>"; }};'
    )
fileref_lines.append(
    f'\t\t{ids["fileref_Assets.xcassets"]} /* Assets.xcassets */ = '
    f'{{isa = PBXFileReference; lastKnownFileType = folder.assetcatalog; path = Assets.xcassets; sourceTree = "<group>"; }};'
)
fileref_lines.append(
    f'\t\t{ids["fileref_PrivacyInfo.xcprivacy"]} /* PrivacyInfo.xcprivacy */ = '
    f'{{isa = PBXFileReference; lastKnownFileType = text.plist.xml; path = PrivacyInfo.xcprivacy; sourceTree = "<group>"; }};'
)
fileref_lines.append(
    f'\t\t{ids["fileref_PreviewAssets.xcassets"]} /* Preview Assets.xcassets */ = '
    f'{{isa = PBXFileReference; lastKnownFileType = folder.assetcatalog; path = "Preview Assets.xcassets"; sourceTree = "<group>"; }};'
)
fileref_lines.append(
    f'\t\t{ids["fileref_product"]} /* TodoNotes.app */ = '
    f'{{isa = PBXFileReference; explicitFileType = wrapper.application; includeInIndex = 0; path = TodoNotes.app; sourceTree = BUILT_PRODUCTS_DIR; }};'
)

# ---- PBXGroup -------------------------------------------------------------
models_children = " ".join(
    f'{ids[f"fileref_{f}"]} /* {f} */,' for f, g in swift_files if g == "Models"
)
store_children = " ".join(
    f'{ids[f"fileref_{f}"]} /* {f} */,' for f, g in swift_files if g == "Store"
)
views_children = " ".join(
    f'{ids[f"fileref_{f}"]} /* {f} */,' for f, g in swift_files if g == "Views"
)

group_lines = f'''\t\t{ids["group_main"]} = {{
\t\t\tisa = PBXGroup;
\t\t\tchildren = (
\t\t\t\t{ids["group_TodoNotes"]} /* TodoNotes */,
\t\t\t\t{ids["group_Products"]} /* Products */,
\t\t\t);
\t\t\tsourceTree = "<group>";
\t\t}};
\t\t{ids["group_TodoNotes"]} /* TodoNotes */ = {{
\t\t\tisa = PBXGroup;
\t\t\tchildren = (
\t\t\t\t{ids["fileref_TodoNotesApp.swift"]} /* TodoNotesApp.swift */,
\t\t\t\t{ids["group_Models"]} /* Models */,
\t\t\t\t{ids["group_Store"]} /* Store */,
\t\t\t\t{ids["group_Views"]} /* Views */,
\t\t\t\t{ids["fileref_Assets.xcassets"]} /* Assets.xcassets */,
\t\t\t\t{ids["fileref_PrivacyInfo.xcprivacy"]} /* PrivacyInfo.xcprivacy */,
\t\t\t\t{ids["group_PreviewContent"]} /* Preview Content */,
\t\t\t);
\t\t\tpath = TodoNotes;
\t\t\tsourceTree = "<group>";
\t\t}};
\t\t{ids["group_Models"]} /* Models */ = {{
\t\t\tisa = PBXGroup;
\t\t\tchildren = (
\t\t\t\t{models_children}
\t\t\t);
\t\t\tpath = Models;
\t\t\tsourceTree = "<group>";
\t\t}};
\t\t{ids["group_Store"]} /* Store */ = {{
\t\t\tisa = PBXGroup;
\t\t\tchildren = (
\t\t\t\t{store_children}
\t\t\t);
\t\t\tpath = Store;
\t\t\tsourceTree = "<group>";
\t\t}};
\t\t{ids["group_Views"]} /* Views */ = {{
\t\t\tisa = PBXGroup;
\t\t\tchildren = (
\t\t\t\t{views_children}
\t\t\t);
\t\t\tpath = Views;
\t\t\tsourceTree = "<group>";
\t\t}};
\t\t{ids["group_PreviewContent"]} /* Preview Content */ = {{
\t\t\tisa = PBXGroup;
\t\t\tchildren = (
\t\t\t\t{ids["fileref_PreviewAssets.xcassets"]} /* Preview Assets.xcassets */,
\t\t\t);
\t\t\tpath = "Preview Content";
\t\t\tsourceTree = "<group>";
\t\t}};
\t\t{ids["group_Products"]} /* Products */ = {{
\t\t\tisa = PBXGroup;
\t\t\tchildren = (
\t\t\t\t{ids["fileref_product"]} /* TodoNotes.app */,
\t\t\t);
\t\t\tname = Products;
\t\t\tsourceTree = "<group>";
\t\t}};'''

# ---- Build phases -----------------------------------------------------
sources_files = "\n".join(
    f'\t\t\t\t{ids[f"buildfile_{f}"]} /* {f} in Sources */,' for f, _ in swift_files
)
sources_phase = f'''\t\t{ids["phase_sources"]} /* Sources */ = {{
\t\t\tisa = PBXSourcesBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
{sources_files}
\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};'''

frameworks_phase = f'''\t\t{ids["phase_frameworks"]} /* Frameworks */ = {{
\t\t\tisa = PBXFrameworksBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};'''

resources_phase = f'''\t\t{ids["phase_resources"]} /* Resources */ = {{
\t\t\tisa = PBXResourcesBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
\t\t\t\t{ids["buildfile_Assets.xcassets"]} /* Assets.xcassets in Resources */,
\t\t\t\t{ids["buildfile_PrivacyInfo.xcprivacy"]} /* PrivacyInfo.xcprivacy in Resources */,
\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};'''

# ---- Target -------------------------------------------------------------
target = f'''\t\t{ids["target"]} /* TodoNotes */ = {{
\t\t\tisa = PBXNativeTarget;
\t\t\tbuildConfigurationList = {ids["configlist_target"]} /* Build configuration list for PBXNativeTarget "TodoNotes" */;
\t\t\tbuildPhases = (
\t\t\t\t{ids["phase_sources"]} /* Sources */,
\t\t\t\t{ids["phase_frameworks"]} /* Frameworks */,
\t\t\t\t{ids["phase_resources"]} /* Resources */,
\t\t\t);
\t\t\tbuildRules = (
\t\t\t);
\t\t\tdependencies = (
\t\t\t);
\t\t\tname = TodoNotes;
\t\t\tproductName = TodoNotes;
\t\t\tproductReference = {ids["fileref_product"]} /* TodoNotes.app */;
\t\t\tproductType = "com.apple.product-type.application";
\t\t}};'''

# ---- Project --------------------------------------------------------------
project = f'''\t\t{ids["project"]} /* Project object */ = {{
\t\t\tisa = PBXProject;
\t\t\tattributes = {{
\t\t\t\tBuildIndependentTargetsInParallel = 1;
\t\t\t\tLastSwiftUpdateCheck = 1500;
\t\t\t\tLastUpgradeCheck = 1500;
\t\t\t\tTargetAttributes = {{
\t\t\t\t\t{ids["target"]} = {{
\t\t\t\t\t\tCreatedOnToolsVersion = 15.0;
\t\t\t\t\t}};
\t\t\t\t}};
\t\t\t}};
\t\t\tbuildConfigurationList = {ids["configlist_project"]} /* Build configuration list for PBXProject "TodoNotes" */;
\t\t\tcompatibilityVersion = "Xcode 14.0";
\t\t\tdevelopmentRegion = ja;
\t\t\thasScannedForEncodings = 0;
\t\t\tknownRegions = (
\t\t\t\tja,
\t\t\t\tBase,
\t\t\t);
\t\t\tmainGroup = {ids["group_main"]};
\t\t\tproductRefGroup = {ids["group_Products"]} /* Products */;
\t\t\tprojectDirPath = "";
\t\t\tprojectRoot = "";
\t\t\ttargets = (
\t\t\t\t{ids["target"]} /* TodoNotes */,
\t\t\t);
\t\t}};'''

# ---- Build configurations --------------------------------------------------
project_debug = f'''\t\t{ids["config_project_debug"]} /* Debug */ = {{
\t\t\tisa = XCBuildConfiguration;
\t\t\tbuildSettings = {{
\t\t\t\tALWAYS_SEARCH_USER_PATHS = NO;
\t\t\t\tASSETCATALOG_COMPILER_GENERATE_SWIFT_ASSET_SYMBOL_EXTENSIONS = YES;
\t\t\t\tCLANG_ANALYZER_NONNULL = YES;
\t\t\t\tCLANG_ANALYZER_NUMBER_OBJECT_CONVERSION = YES_AGGRESSIVE;
\t\t\t\tCLANG_CXX_LANGUAGE_STANDARD = "gnu++20";
\t\t\t\tCLANG_ENABLE_MODULES = YES;
\t\t\t\tCLANG_ENABLE_OBJC_ARC = YES;
\t\t\t\tCLANG_ENABLE_OBJC_WEAK = YES;
\t\t\t\tCLANG_WARN_BLOCK_CAPTURE_AUTORELEASING = YES;
\t\t\t\tCLANG_WARN_BOOL_CONVERSION = YES;
\t\t\t\tCLANG_WARN_COMMA = YES;
\t\t\t\tCLANG_WARN_CONSTANT_CONVERSION = YES;
\t\t\t\tCLANG_WARN_DEPRECATED_OBJC_IMPLEMENTATIONS = YES;
\t\t\t\tCLANG_WARN_DIRECT_OBJC_ISA_USAGE = YES_ERROR;
\t\t\t\tCLANG_WARN_DOCUMENTATION_COMMENTS = YES;
\t\t\t\tCLANG_WARN_EMPTY_BODY = YES;
\t\t\t\tCLANG_WARN_ENUM_CONVERSION = YES;
\t\t\t\tCLANG_WARN_INFINITE_RECURSION = YES;
\t\t\t\tCLANG_WARN_INT_CONVERSION = YES;
\t\t\t\tCLANG_WARN_NON_LITERAL_NULL_CONVERSION = YES;
\t\t\t\tCLANG_WARN_OBJC_IMPLICIT_RETAIN_SELF = YES;
\t\t\t\tCLANG_WARN_OBJC_LITERAL_CONVERSION = YES;
\t\t\t\tCLANG_WARN_OBJC_ROOT_CLASS = YES_ERROR;
\t\t\t\tCLANG_WARN_QUOTED_INCLUDE_IN_FRAMEWORK_HEADER = YES;
\t\t\t\tCLANG_WARN_RANGE_LOOP_ANALYSIS = YES;
\t\t\t\tCLANG_WARN_STRICT_PROTOTYPES = YES;
\t\t\t\tCLANG_WARN_SUSPICIOUS_MOVE = YES;
\t\t\t\tCLANG_WARN_UNGUARDED_AVAILABILITY = YES_AGGRESSIVE;
\t\t\t\tCLANG_WARN_UNREACHABLE_CODE = YES;
\t\t\t\tCLANG_WARN__DUPLICATE_METHOD_MATCH = YES;
\t\t\t\tCOPY_PHASE_STRIP = NO;
\t\t\t\tDEBUG_INFORMATION_FORMAT = dwarf;
\t\t\t\tENABLE_STRICT_OBJC_MSGSEND = YES;
\t\t\t\tENABLE_TESTABILITY = YES;
\t\t\t\tENABLE_USER_SCRIPT_SANDBOXING = YES;
\t\t\t\tGCC_C_LANGUAGE_STANDARD = gnu17;
\t\t\t\tGCC_DYNAMIC_NO_PIC = NO;
\t\t\t\tGCC_NO_COMMON_BLOCKS = YES;
\t\t\t\tGCC_OPTIMIZATION_LEVEL = 0;
\t\t\t\tGCC_PREPROCESSOR_DEFINITIONS = (
\t\t\t\t\t"DEBUG=1",
\t\t\t\t\t"$(inherited)",
\t\t\t\t);
\t\t\t\tGCC_WARN_64_TO_32_BIT_CONVERSION = YES;
\t\t\t\tGCC_WARN_ABOUT_RETURN_TYPE = YES_ERROR;
\t\t\t\tGCC_WARN_UNDECLARED_SELECTOR = YES;
\t\t\t\tGCC_WARN_UNINITIALIZED_AUTOS = YES_AGGRESSIVE;
\t\t\t\tGCC_WARN_UNUSED_FUNCTION = YES;
\t\t\t\tGCC_WARN_UNUSED_VARIABLE = YES;
\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = 16.0;
\t\t\t\tMTL_ENABLE_DEBUG_INFO = INCLUDE_SOURCE;
\t\t\t\tMTL_FAST_MATH = YES;
\t\t\t\tONLY_ACTIVE_ARCH = YES;
\t\t\t\tSDKROOT = iphoneos;
\t\t\t\tSWIFT_ACTIVE_COMPILATION_CONDITIONS = "DEBUG $(inherited)";
\t\t\t\tSWIFT_OPTIMIZATION_LEVEL = "-Onone";
\t\t\t}};
\t\t\tname = Debug;
\t\t}};'''

project_release = f'''\t\t{ids["config_project_release"]} /* Release */ = {{
\t\t\tisa = XCBuildConfiguration;
\t\t\tbuildSettings = {{
\t\t\t\tALWAYS_SEARCH_USER_PATHS = NO;
\t\t\t\tASSETCATALOG_COMPILER_GENERATE_SWIFT_ASSET_SYMBOL_EXTENSIONS = YES;
\t\t\t\tCLANG_ANALYZER_NONNULL = YES;
\t\t\t\tCLANG_ANALYZER_NUMBER_OBJECT_CONVERSION = YES_AGGRESSIVE;
\t\t\t\tCLANG_CXX_LANGUAGE_STANDARD = "gnu++20";
\t\t\t\tCLANG_ENABLE_MODULES = YES;
\t\t\t\tCLANG_ENABLE_OBJC_ARC = YES;
\t\t\t\tCLANG_ENABLE_OBJC_WEAK = YES;
\t\t\t\tCLANG_WARN_BLOCK_CAPTURE_AUTORELEASING = YES;
\t\t\t\tCLANG_WARN_BOOL_CONVERSION = YES;
\t\t\t\tCLANG_WARN_COMMA = YES;
\t\t\t\tCLANG_WARN_CONSTANT_CONVERSION = YES;
\t\t\t\tCLANG_WARN_DEPRECATED_OBJC_IMPLEMENTATIONS = YES;
\t\t\t\tCLANG_WARN_DIRECT_OBJC_ISA_USAGE = YES_ERROR;
\t\t\t\tCLANG_WARN_DOCUMENTATION_COMMENTS = YES;
\t\t\t\tCLANG_WARN_EMPTY_BODY = YES;
\t\t\t\tCLANG_WARN_ENUM_CONVERSION = YES;
\t\t\t\tCLANG_WARN_INFINITE_RECURSION = YES;
\t\t\t\tCLANG_WARN_INT_CONVERSION = YES;
\t\t\t\tCLANG_WARN_NON_LITERAL_NULL_CONVERSION = YES;
\t\t\t\tCLANG_WARN_OBJC_IMPLICIT_RETAIN_SELF = YES;
\t\t\t\tCLANG_WARN_OBJC_LITERAL_CONVERSION = YES;
\t\t\t\tCLANG_WARN_OBJC_ROOT_CLASS = YES_ERROR;
\t\t\t\tCLANG_WARN_QUOTED_INCLUDE_IN_FRAMEWORK_HEADER = YES;
\t\t\t\tCLANG_WARN_RANGE_LOOP_ANALYSIS = YES;
\t\t\t\tCLANG_WARN_STRICT_PROTOTYPES = YES;
\t\t\t\tCLANG_WARN_SUSPICIOUS_MOVE = YES;
\t\t\t\tCLANG_WARN_UNGUARDED_AVAILABILITY = YES_AGGRESSIVE;
\t\t\t\tCLANG_WARN_UNREACHABLE_CODE = YES;
\t\t\t\tCLANG_WARN__DUPLICATE_METHOD_MATCH = YES;
\t\t\t\tCOPY_PHASE_STRIP = NO;
\t\t\t\tDEBUG_INFORMATION_FORMAT = "dwarf-with-dsym";
\t\t\t\tENABLE_NS_ASSERTIONS = NO;
\t\t\t\tENABLE_STRICT_OBJC_MSGSEND = YES;
\t\t\t\tENABLE_USER_SCRIPT_SANDBOXING = YES;
\t\t\t\tGCC_C_LANGUAGE_STANDARD = gnu17;
\t\t\t\tGCC_NO_COMMON_BLOCKS = YES;
\t\t\t\tGCC_WARN_64_TO_32_BIT_CONVERSION = YES;
\t\t\t\tGCC_WARN_ABOUT_RETURN_TYPE = YES_ERROR;
\t\t\t\tGCC_WARN_UNDECLARED_SELECTOR = YES;
\t\t\t\tGCC_WARN_UNINITIALIZED_AUTOS = YES_AGGRESSIVE;
\t\t\t\tGCC_WARN_UNUSED_FUNCTION = YES;
\t\t\t\tGCC_WARN_UNUSED_VARIABLE = YES;
\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = 16.0;
\t\t\t\tMTL_ENABLE_DEBUG_INFO = NO;
\t\t\t\tMTL_FAST_MATH = YES;
\t\t\t\tSDKROOT = iphoneos;
\t\t\t\tSWIFT_COMPILATION_MODE = wholemodule;
\t\t\t\tVALIDATE_PRODUCT = YES;
\t\t\t}};
\t\t\tname = Release;
\t\t}};'''

target_debug = f'''\t\t{ids["config_target_debug"]} /* Debug */ = {{
\t\t\tisa = XCBuildConfiguration;
\t\t\tbuildSettings = {{
\t\t\t\tASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;
\t\t\t\tASSETCATALOG_COMPILER_GLOBAL_ACCENT_COLOR_NAME = AccentColor;
\t\t\t\tCODE_SIGN_STYLE = Automatic;
\t\t\t\tCURRENT_PROJECT_VERSION = 1;
\t\t\t\tDEVELOPMENT_ASSET_PATHS = "\\"TodoNotes/Preview Content\\"";
\t\t\t\tENABLE_PREVIEWS = YES;
\t\t\t\tGENERATE_INFOPLIST_FILE = YES;
\t\t\t\tINFOPLIST_KEY_CFBundleDisplayName = "Todoメモ";
\t\t\t\tINFOPLIST_KEY_LSApplicationCategoryType = "public.app-category.productivity";
\t\t\t\tINFOPLIST_KEY_UIApplicationSceneManifest_Generation = YES;
\t\t\t\tINFOPLIST_KEY_UIApplicationSupportsIndirectInputEvents = YES;
\t\t\t\tINFOPLIST_KEY_UILaunchScreen_Generation = YES;
\t\t\t\tINFOPLIST_KEY_UISupportedInterfaceOrientations_iPad = "UIInterfaceOrientationPortrait UIInterfaceOrientationPortraitUpsideDown UIInterfaceOrientationLandscapeLeft UIInterfaceOrientationLandscapeRight";
\t\t\t\tINFOPLIST_KEY_UISupportedInterfaceOrientations_iPhone = "UIInterfaceOrientationPortrait";
\t\t\t\tLD_RUNPATH_SEARCH_PATHS = (
\t\t\t\t\t"$(inherited)",
\t\t\t\t\t"@executable_path/Frameworks",
\t\t\t\t);
\t\t\t\tMARKETING_VERSION = 1.0;
\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = "com.yukitakano.todonotes";
\t\t\t\tPRODUCT_NAME = "$(TARGET_NAME)";
\t\t\t\tSWIFT_EMIT_LOC_STRINGS = YES;
\t\t\t\tSWIFT_VERSION = 5.0;
\t\t\t\tTARGETED_DEVICE_FAMILY = "1,2";
\t\t\t}};
\t\t\tname = Debug;
\t\t}};'''

target_release = f'''\t\t{ids["config_target_release"]} /* Release */ = {{
\t\t\tisa = XCBuildConfiguration;
\t\t\tbuildSettings = {{
\t\t\t\tASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;
\t\t\t\tASSETCATALOG_COMPILER_GLOBAL_ACCENT_COLOR_NAME = AccentColor;
\t\t\t\tCODE_SIGN_STYLE = Automatic;
\t\t\t\tCURRENT_PROJECT_VERSION = 1;
\t\t\t\tDEVELOPMENT_ASSET_PATHS = "\\"TodoNotes/Preview Content\\"";
\t\t\t\tENABLE_PREVIEWS = YES;
\t\t\t\tGENERATE_INFOPLIST_FILE = YES;
\t\t\t\tINFOPLIST_KEY_CFBundleDisplayName = "Todoメモ";
\t\t\t\tINFOPLIST_KEY_LSApplicationCategoryType = "public.app-category.productivity";
\t\t\t\tINFOPLIST_KEY_UIApplicationSceneManifest_Generation = YES;
\t\t\t\tINFOPLIST_KEY_UIApplicationSupportsIndirectInputEvents = YES;
\t\t\t\tINFOPLIST_KEY_UILaunchScreen_Generation = YES;
\t\t\t\tINFOPLIST_KEY_UISupportedInterfaceOrientations_iPad = "UIInterfaceOrientationPortrait UIInterfaceOrientationPortraitUpsideDown UIInterfaceOrientationLandscapeLeft UIInterfaceOrientationLandscapeRight";
\t\t\t\tINFOPLIST_KEY_UISupportedInterfaceOrientations_iPhone = "UIInterfaceOrientationPortrait";
\t\t\t\tLD_RUNPATH_SEARCH_PATHS = (
\t\t\t\t\t"$(inherited)",
\t\t\t\t\t"@executable_path/Frameworks",
\t\t\t\t);
\t\t\t\tMARKETING_VERSION = 1.0;
\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = "com.yukitakano.todonotes";
\t\t\t\tPRODUCT_NAME = "$(TARGET_NAME)";
\t\t\t\tSWIFT_EMIT_LOC_STRINGS = YES;
\t\t\t\tSWIFT_VERSION = 5.0;
\t\t\t\tTARGETED_DEVICE_FAMILY = "1,2";
\t\t\t}};
\t\t\tname = Release;
\t\t}};'''

configlist_project = f'''\t\t{ids["configlist_project"]} /* Build configuration list for PBXProject "TodoNotes" */ = {{
\t\t\tisa = XCConfigurationList;
\t\t\tbuildConfigurations = (
\t\t\t\t{ids["config_project_debug"]} /* Debug */,
\t\t\t\t{ids["config_project_release"]} /* Release */,
\t\t\t);
\t\t\tdefaultConfigurationIsVisible = 0;
\t\t\tdefaultConfigurationName = Release;
\t\t}};'''

configlist_target = f'''\t\t{ids["configlist_target"]} /* Build configuration list for PBXNativeTarget "TodoNotes" */ = {{
\t\t\tisa = XCConfigurationList;
\t\t\tbuildConfigurations = (
\t\t\t\t{ids["config_target_debug"]} /* Debug */,
\t\t\t\t{ids["config_target_release"]} /* Release */,
\t\t\t);
\t\t\tdefaultConfigurationIsVisible = 0;
\t\t\tdefaultConfigurationName = Release;
\t\t}};'''

# ---- assemble ---------------------------------------------------------
out = []
out.append("// !$*UTF8*$!")
out.append("{")
out.append("\tarchiveVersion = 1;")
out.append("\tclasses = {")
out.append("\t};")
out.append("\tobjectVersion = 56;")
out.append("\tobjects = {")

out.append("\n/* Begin PBXBuildFile section */")
out.extend(buildfile_lines)
out.append("/* End PBXBuildFile section */")

out.append("\n/* Begin PBXFileReference section */")
out.extend(fileref_lines)
out.append("/* End PBXFileReference section */")

out.append("\n/* Begin PBXFrameworksBuildPhase section */")
out.append(frameworks_phase)
out.append("/* End PBXFrameworksBuildPhase section */")

out.append("\n/* Begin PBXGroup section */")
out.append(group_lines)
out.append("/* End PBXGroup section */")

out.append("\n/* Begin PBXNativeTarget section */")
out.append(target)
out.append("/* End PBXNativeTarget section */")

out.append("\n/* Begin PBXProject section */")
out.append(project)
out.append("/* End PBXProject section */")

out.append("\n/* Begin PBXResourcesBuildPhase section */")
out.append(resources_phase)
out.append("/* End PBXResourcesBuildPhase section */")

out.append("\n/* Begin PBXSourcesBuildPhase section */")
out.append(sources_phase)
out.append("/* End PBXSourcesBuildPhase section */")

out.append("\n/* Begin XCBuildConfiguration section */")
out.append(project_debug)
out.append(project_release)
out.append(target_debug)
out.append(target_release)
out.append("/* End XCBuildConfiguration section */")

out.append("\n/* Begin XCConfigurationList section */")
out.append(configlist_project)
out.append(configlist_target)
out.append("/* End XCConfigurationList section */")

out.append("\t};")
out.append(f'\trootObject = {ids["project"]} /* Project object */;')
out.append("}")

text = "\n".join(out) + "\n"

with open("TodoNotes.xcodeproj/project.pbxproj", "w") as f:
    f.write(text)

print("Wrote TodoNotes.xcodeproj/project.pbxproj")
print("Total objects:", len(ids))
