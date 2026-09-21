#!/usr/bin/env python3
"""Generates TodoNotes.xcodeproj/project.pbxproj from scratch.

This is a one-off generator (no Xcode available in this environment to
produce the project file the normal way). It defines two targets:
  - TodoNotes: the main iOS app
  - TodoNotesWidgetExtension: the WidgetKit extension (Lock Screen +
    Home Screen widget), embedded into the app and sharing model code
    via files that belong to both targets' Sources build phase.

Run with: python3 scripts/generate_pbxproj.py

IDs are derived deterministically from each object's name (a truncated
SHA-256 hash), not random, so re-running this script after an unrelated
edit produces the *same* ids for existing objects. That matters because
the checked-in .xcscheme files hardcode target ids — if those shifted on
every regeneration, the scheme would silently point at nothing.
"""
import hashlib

ids = {}
def new_id(name):
    i = hashlib.sha256(name.encode()).hexdigest().upper()[:24]
    ids[name] = i
    return i

# ---------------------------------------------------------------------
# File inventory
# ---------------------------------------------------------------------

# (path relative to project root, group path e.g. "TodoNotes/Models",
#  set of target keys it's compiled into: "app", "widget")
SWIFT_FILES = [
    ("TodoNotes/TodoNotesApp.swift", "TodoNotes", {"app"}),
    ("TodoNotes/Models/TodoItem.swift", "TodoNotes/Models", {"app", "widget"}),
    ("TodoNotes/Models/NoteColor.swift", "TodoNotes/Models", {"app", "widget"}),
    ("TodoNotes/Models/TodoNote.swift", "TodoNotes/Models", {"app", "widget"}),
    ("TodoNotes/Shared/AppGroup.swift", "TodoNotes/Shared", {"app", "widget"}),
    ("TodoNotes/Shared/NotesRepository.swift", "TodoNotes/Shared", {"app", "widget"}),
    ("TodoNotes/Shared/WidgetKind.swift", "TodoNotes/Shared", {"app", "widget"}),
    ("TodoNotes/Shared/NotificationManager.swift", "TodoNotes/Shared", {"app", "widget"}),
    ("TodoNotes/Store/NoteStore.swift", "TodoNotes/Store", {"app"}),
    ("TodoNotes/Store/Haptics.swift", "TodoNotes/Store", {"app"}),
    ("TodoNotes/Views/ContentView.swift", "TodoNotes/Views", {"app"}),
    ("TodoNotes/Views/NoteCardView.swift", "TodoNotes/Views", {"app"}),
    ("TodoNotes/Views/ColorPickerRow.swift", "TodoNotes/Views", {"app"}),
    ("TodoNotes/Views/NoteEditorView.swift", "TodoNotes/Views", {"app"}),
    # Compiled into the app too (not just the widget extension) so
    # WidgetPreviewHarness (DEBUG-only) can render the real widget view
    # for CI screenshots. TodoNotesWidget.swift stays widget-only since
    # it declares the extension's @main entry point.
    ("TodoNotes/WidgetPreviewHarness.swift", "TodoNotes", {"app"}),
    ("TodoNotesWidget/TodoNotesWidget.swift", "TodoNotesWidget", {"widget"}),
    ("TodoNotesWidget/Provider.swift", "TodoNotesWidget", {"widget", "app"}),
    ("TodoNotesWidget/TodoNotesWidgetView.swift", "TodoNotesWidget", {"widget", "app"}),
    ("TodoNotesWidget/ToggleTodoItemIntent.swift", "TodoNotesWidget", {"widget", "app"}),
]

# Non-source files that are Resources build-phase members.
RESOURCE_FILES = [
    ("TodoNotes/Assets.xcassets", "TodoNotes", "folder.assetcatalog", {"app"}),
    ("TodoNotes/PrivacyInfo.xcprivacy", "TodoNotes", "text.plist.xml", {"app"}),
    ("TodoNotesWidget/PrivacyInfo.xcprivacy", "TodoNotesWidget", "text.plist.xml", {"widget"}),
]

# Files that appear in the navigator but aren't in any build phase
# (referenced instead via a build setting like INFOPLIST_FILE or
# CODE_SIGN_ENTITLEMENTS).
REFERENCE_ONLY_FILES = [
    ("TodoNotes/TodoNotes.entitlements", "TodoNotes", "text.plist.xml"),
    ("TodoNotesWidget/Info.plist", "TodoNotesWidget", "text.plist.xml"),
    ("TodoNotesWidget/TodoNotesWidget.entitlements", "TodoNotesWidget", "text.plist.xml"),
]

# Preview Content is referenced by DEVELOPMENT_ASSET_PATHS, not a build phase.
PREVIEW_ASSETS_PATH = "TodoNotes/Preview Content/Preview Assets.xcassets"

# ---------------------------------------------------------------------
# Allocate ids
# ---------------------------------------------------------------------

for path, group, targets in SWIFT_FILES:
    new_id(f"fileref::{path}")
    for t in targets:
        new_id(f"buildfile::{t}::{path}")

for path, group, filetype, targets in RESOURCE_FILES:
    new_id(f"fileref::{path}")
    for t in targets:
        new_id(f"buildfile::{t}::{path}")

for path, group, filetype in REFERENCE_ONLY_FILES:
    new_id(f"fileref::{path}")

new_id(f"fileref::{PREVIEW_ASSETS_PATH}")
new_id("fileref::AccentColor")  # placeholder not used directly; colorset has its own Contents.json, no fileref needed

new_id("fileref_product_app")
new_id("fileref_product_widget")
new_id("buildfile_embed_widget")

# Groups
new_id("group_main")
new_id("group_TodoNotes")
new_id("group_Models")
new_id("group_Shared")
new_id("group_Store")
new_id("group_Views")
new_id("group_PreviewContent")
new_id("group_TodoNotesWidget")
new_id("group_Products")

# Build phases
new_id("phase_sources_app")
new_id("phase_frameworks_app")
new_id("phase_resources_app")
new_id("phase_embed_widget")
new_id("phase_sources_widget")
new_id("phase_frameworks_widget")
new_id("phase_resources_widget")

# Targets / project
new_id("target_app")
new_id("target_widget")
new_id("project")

# Dependency wiring (app -> widget)
new_id("containerItemProxy_widget")
new_id("targetDependency_widget")

# Build configurations
new_id("config_project_debug")
new_id("config_project_release")
new_id("config_app_debug")
new_id("config_app_release")
new_id("config_widget_debug")
new_id("config_widget_release")
new_id("configlist_project")
new_id("configlist_app")
new_id("configlist_widget")

# ---------------------------------------------------------------------
# PBXBuildFile / PBXFileReference
# ---------------------------------------------------------------------

buildfile_lines = []
fileref_lines = []

def basename(path):
    return path.rsplit("/", 1)[-1]

for path, group, targets in SWIFT_FILES:
    name = basename(path)
    fileref_lines.append(
        f'\t\t{ids[f"fileref::{path}"]} /* {name} */ = '
        f'{{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = {name}; sourceTree = "<group>"; }};'
    )
    for t in targets:
        buildfile_lines.append(
            f'\t\t{ids[f"buildfile::{t}::{path}"]} /* {name} in Sources */ = '
            f'{{isa = PBXBuildFile; fileRef = {ids[f"fileref::{path}"]} /* {name} */; }};'
        )

for path, group, filetype, targets in RESOURCE_FILES:
    name = basename(path)
    fileref_lines.append(
        f'\t\t{ids[f"fileref::{path}"]} /* {name} */ = '
        f'{{isa = PBXFileReference; lastKnownFileType = {filetype}; path = {name}; sourceTree = "<group>"; }};'
    )
    for t in targets:
        buildfile_lines.append(
            f'\t\t{ids[f"buildfile::{t}::{path}"]} /* {name} in Resources */ = '
            f'{{isa = PBXBuildFile; fileRef = {ids[f"fileref::{path}"]} /* {name} */; }};'
        )

for path, group, filetype in REFERENCE_ONLY_FILES:
    name = basename(path)
    fileref_lines.append(
        f'\t\t{ids[f"fileref::{path}"]} /* {name} */ = '
        f'{{isa = PBXFileReference; lastKnownFileType = {filetype}; path = {name}; sourceTree = "<group>"; }};'
    )

fileref_lines.append(
    f'\t\t{ids[f"fileref::{PREVIEW_ASSETS_PATH}"]} /* Preview Assets.xcassets */ = '
    f'{{isa = PBXFileReference; lastKnownFileType = folder.assetcatalog; path = "Preview Assets.xcassets"; sourceTree = "<group>"; }};'
)

fileref_lines.append(
    f'\t\t{ids["fileref_product_app"]} /* TodoNotes.app */ = '
    f'{{isa = PBXFileReference; explicitFileType = wrapper.application; includeInIndex = 0; path = TodoNotes.app; sourceTree = BUILT_PRODUCTS_DIR; }};'
)
fileref_lines.append(
    f'\t\t{ids["fileref_product_widget"]} /* TodoNotesWidgetExtension.appex */ = '
    f'{{isa = PBXFileReference; explicitFileType = "wrapper.app-extension"; includeInIndex = 0; path = TodoNotesWidgetExtension.appex; sourceTree = BUILT_PRODUCTS_DIR; }};'
)

buildfile_lines.append(
    f'\t\t{ids["buildfile_embed_widget"]} /* TodoNotesWidgetExtension.appex in Embed Foundation Extensions */ = '
    f'{{isa = PBXBuildFile; fileRef = {ids["fileref_product_widget"]} /* TodoNotesWidgetExtension.appex */; '
    f'settings = {{ATTRIBUTES = (RemoveHeaderOnCopy, ); }}; }};'
)

# ---------------------------------------------------------------------
# PBXGroup
# ---------------------------------------------------------------------

def children_for(group_path, exclude_reference_only=False):
    refs = []
    for path, g, targets in SWIFT_FILES:
        if g == group_path:
            refs.append(f'{ids[f"fileref::{path}"]} /* {basename(path)} */,')
    for path, g, filetype, targets in RESOURCE_FILES:
        if g == group_path:
            refs.append(f'{ids[f"fileref::{path}"]} /* {basename(path)} */,')
    for path, g, filetype in REFERENCE_ONLY_FILES:
        if g == group_path:
            refs.append(f'{ids[f"fileref::{path}"]} /* {basename(path)} */,')
    return "\n\t\t\t\t".join(refs)

models_children = children_for("TodoNotes/Models")
shared_children = children_for("TodoNotes/Shared")
store_children = children_for("TodoNotes/Store")
views_children = children_for("TodoNotes/Views")
widget_children = children_for("TodoNotesWidget")

group_lines = f'''\t\t{ids["group_main"]} = {{
\t\t\tisa = PBXGroup;
\t\t\tchildren = (
\t\t\t\t{ids["group_TodoNotes"]} /* TodoNotes */,
\t\t\t\t{ids["group_TodoNotesWidget"]} /* TodoNotesWidget */,
\t\t\t\t{ids["group_Products"]} /* Products */,
\t\t\t);
\t\t\tsourceTree = "<group>";
\t\t}};
\t\t{ids["group_TodoNotes"]} /* TodoNotes */ = {{
\t\t\tisa = PBXGroup;
\t\t\tchildren = (
\t\t\t\t{ids['fileref::TodoNotes/TodoNotesApp.swift']} /* TodoNotesApp.swift */,
\t\t\t\t{ids['fileref::TodoNotes/WidgetPreviewHarness.swift']} /* WidgetPreviewHarness.swift */,
\t\t\t\t{ids["group_Models"]} /* Models */,
\t\t\t\t{ids["group_Shared"]} /* Shared */,
\t\t\t\t{ids["group_Store"]} /* Store */,
\t\t\t\t{ids["group_Views"]} /* Views */,
\t\t\t\t{ids['fileref::TodoNotes/Assets.xcassets']} /* Assets.xcassets */,
\t\t\t\t{ids['fileref::TodoNotes/PrivacyInfo.xcprivacy']} /* PrivacyInfo.xcprivacy */,
\t\t\t\t{ids['fileref::TodoNotes/TodoNotes.entitlements']} /* TodoNotes.entitlements */,
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
\t\t{ids["group_Shared"]} /* Shared */ = {{
\t\t\tisa = PBXGroup;
\t\t\tchildren = (
\t\t\t\t{shared_children}
\t\t\t);
\t\t\tpath = Shared;
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
\t\t\t\t{ids[f"fileref::{PREVIEW_ASSETS_PATH}"]} /* Preview Assets.xcassets */,
\t\t\t);
\t\t\tpath = "Preview Content";
\t\t\tsourceTree = "<group>";
\t\t}};
\t\t{ids["group_TodoNotesWidget"]} /* TodoNotesWidget */ = {{
\t\t\tisa = PBXGroup;
\t\t\tchildren = (
\t\t\t\t{widget_children}
\t\t\t);
\t\t\tpath = TodoNotesWidget;
\t\t\tsourceTree = "<group>";
\t\t}};
\t\t{ids["group_Products"]} /* Products */ = {{
\t\t\tisa = PBXGroup;
\t\t\tchildren = (
\t\t\t\t{ids["fileref_product_app"]} /* TodoNotes.app */,
\t\t\t\t{ids["fileref_product_widget"]} /* TodoNotesWidgetExtension.appex */,
\t\t\t);
\t\t\tname = Products;
\t\t\tsourceTree = "<group>";
\t\t}};'''

# ---------------------------------------------------------------------
# Build phases
# ---------------------------------------------------------------------

def sources_phase(phase_id, name, target_key):
    files = []
    for path, group, targets in SWIFT_FILES:
        if target_key in targets:
            files.append(f'\t\t\t\t{ids[f"buildfile::{target_key}::{path}"]} /* {basename(path)} in Sources */,')
    files_block = "\n".join(files)
    return f'''\t\t{phase_id} /* Sources */ = {{
\t\t\tisa = PBXSourcesBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
{files_block}
\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};'''

def resources_phase(phase_id, name, target_key):
    files = []
    for path, group, filetype, targets in RESOURCE_FILES:
        if target_key in targets:
            files.append(f'\t\t\t\t{ids[f"buildfile::{target_key}::{path}"]} /* {basename(path)} in Resources */,')
    files_block = "\n".join(files)
    return f'''\t\t{phase_id} /* Resources */ = {{
\t\t\tisa = PBXResourcesBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
{files_block}
\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};'''

def frameworks_phase(phase_id):
    return f'''\t\t{phase_id} /* Frameworks */ = {{
\t\t\tisa = PBXFrameworksBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};'''

sources_phase_app = sources_phase(ids["phase_sources_app"], "Sources", "app")
sources_phase_widget = sources_phase(ids["phase_sources_widget"], "Sources", "widget")
resources_phase_app = resources_phase(ids["phase_resources_app"], "Resources", "app")
resources_phase_widget = resources_phase(ids["phase_resources_widget"], "Resources", "widget")
frameworks_phase_app = frameworks_phase(ids["phase_frameworks_app"])
frameworks_phase_widget = frameworks_phase(ids["phase_frameworks_widget"])

embed_widget_phase = f'''\t\t{ids["phase_embed_widget"]} /* Embed Foundation Extensions */ = {{
\t\t\tisa = PBXCopyFilesBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tdstPath = "";
\t\t\tdstSubfolderSpec = 13;
\t\t\tfiles = (
\t\t\t\t{ids["buildfile_embed_widget"]} /* TodoNotesWidgetExtension.appex in Embed Foundation Extensions */,
\t\t\t);
\t\t\tname = "Embed Foundation Extensions";
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};'''

# ---------------------------------------------------------------------
# Targets / dependency wiring
# ---------------------------------------------------------------------

container_item_proxy = f'''\t\t{ids["containerItemProxy_widget"]} /* PBXContainerItemProxy */ = {{
\t\t\tisa = PBXContainerItemProxy;
\t\t\tcontainerPortal = {ids["project"]} /* Project object */;
\t\t\tproxyType = 1;
\t\t\tremoteGlobalIDString = {ids["target_widget"]};
\t\t\tremoteInfo = TodoNotesWidgetExtension;
\t\t}};'''

target_dependency = f'''\t\t{ids["targetDependency_widget"]} /* PBXTargetDependency */ = {{
\t\t\tisa = PBXTargetDependency;
\t\t\ttarget = {ids["target_widget"]} /* TodoNotesWidgetExtension */;
\t\t\ttargetProxy = {ids["containerItemProxy_widget"]} /* PBXContainerItemProxy */;
\t\t}};'''

target_app = f'''\t\t{ids["target_app"]} /* TodoNotes */ = {{
\t\t\tisa = PBXNativeTarget;
\t\t\tbuildConfigurationList = {ids["configlist_app"]} /* Build configuration list for PBXNativeTarget "TodoNotes" */;
\t\t\tbuildPhases = (
\t\t\t\t{ids["phase_sources_app"]} /* Sources */,
\t\t\t\t{ids["phase_frameworks_app"]} /* Frameworks */,
\t\t\t\t{ids["phase_resources_app"]} /* Resources */,
\t\t\t\t{ids["phase_embed_widget"]} /* Embed Foundation Extensions */,
\t\t\t);
\t\t\tbuildRules = (
\t\t\t);
\t\t\tdependencies = (
\t\t\t\t{ids["targetDependency_widget"]} /* PBXTargetDependency */,
\t\t\t);
\t\t\tname = TodoNotes;
\t\t\tproductName = TodoNotes;
\t\t\tproductReference = {ids["fileref_product_app"]} /* TodoNotes.app */;
\t\t\tproductType = "com.apple.product-type.application";
\t\t}};'''

target_widget = f'''\t\t{ids["target_widget"]} /* TodoNotesWidgetExtension */ = {{
\t\t\tisa = PBXNativeTarget;
\t\t\tbuildConfigurationList = {ids["configlist_widget"]} /* Build configuration list for PBXNativeTarget "TodoNotesWidgetExtension" */;
\t\t\tbuildPhases = (
\t\t\t\t{ids["phase_sources_widget"]} /* Sources */,
\t\t\t\t{ids["phase_frameworks_widget"]} /* Frameworks */,
\t\t\t\t{ids["phase_resources_widget"]} /* Resources */,
\t\t\t);
\t\t\tbuildRules = (
\t\t\t);
\t\t\tdependencies = (
\t\t\t);
\t\t\tname = TodoNotesWidgetExtension;
\t\t\tproductName = TodoNotesWidgetExtension;
\t\t\tproductReference = {ids["fileref_product_widget"]} /* TodoNotesWidgetExtension.appex */;
\t\t\tproductType = "com.apple.product-type.app-extension";
\t\t}};'''

# ---------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------

project = f'''\t\t{ids["project"]} /* Project object */ = {{
\t\t\tisa = PBXProject;
\t\t\tattributes = {{
\t\t\t\tBuildIndependentTargetsInParallel = 1;
\t\t\t\tLastSwiftUpdateCheck = 1500;
\t\t\t\tLastUpgradeCheck = 1500;
\t\t\t\tTargetAttributes = {{
\t\t\t\t\t{ids["target_app"]} = {{
\t\t\t\t\t\tCreatedOnToolsVersion = 15.0;
\t\t\t\t\t}};
\t\t\t\t\t{ids["target_widget"]} = {{
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
\t\t\t\t{ids["target_app"]} /* TodoNotes */,
\t\t\t\t{ids["target_widget"]} /* TodoNotesWidgetExtension */,
\t\t\t);
\t\t}};'''

# ---------------------------------------------------------------------
# Build configurations
# ---------------------------------------------------------------------

DEPLOYMENT_TARGET = "17.0"

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
\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = {DEPLOYMENT_TARGET};
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
\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = {DEPLOYMENT_TARGET};
\t\t\t\tMTL_ENABLE_DEBUG_INFO = NO;
\t\t\t\tMTL_FAST_MATH = YES;
\t\t\t\tSDKROOT = iphoneos;
\t\t\t\tSWIFT_COMPILATION_MODE = wholemodule;
\t\t\t\tVALIDATE_PRODUCT = YES;
\t\t\t}};
\t\t\tname = Release;
\t\t}};'''

def app_config(config_id, name):
    return f'''\t\t{config_id} /* {name} */ = {{
\t\t\tisa = XCBuildConfiguration;
\t\t\tbuildSettings = {{
\t\t\t\tASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;
\t\t\t\tASSETCATALOG_COMPILER_GLOBAL_ACCENT_COLOR_NAME = AccentColor;
\t\t\t\tCODE_SIGN_ENTITLEMENTS = TodoNotes/TodoNotes.entitlements;
\t\t\t\tCODE_SIGN_STYLE = Automatic;
\t\t\t\tCURRENT_PROJECT_VERSION = 1;
\t\t\t\tDEVELOPMENT_LANGUAGE = ja;
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
\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = {DEPLOYMENT_TARGET};
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
\t\t\tname = {name};
\t\t}};'''

def widget_config(config_id, name):
    return f'''\t\t{config_id} /* {name} */ = {{
\t\t\tisa = XCBuildConfiguration;
\t\t\tbuildSettings = {{
\t\t\t\tCODE_SIGN_ENTITLEMENTS = TodoNotesWidget/TodoNotesWidget.entitlements;
\t\t\t\tCODE_SIGN_STYLE = Automatic;
\t\t\t\tCURRENT_PROJECT_VERSION = 1;
\t\t\t\tDEVELOPMENT_LANGUAGE = ja;
\t\t\t\tGENERATE_INFOPLIST_FILE = NO;
\t\t\t\tINFOPLIST_FILE = TodoNotesWidget/Info.plist;
\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = {DEPLOYMENT_TARGET};
\t\t\t\tLD_RUNPATH_SEARCH_PATHS = (
\t\t\t\t\t"$(inherited)",
\t\t\t\t\t"@executable_path/Frameworks",
\t\t\t\t\t"@executable_path/../../Frameworks",
\t\t\t\t);
\t\t\t\tMARKETING_VERSION = 1.0;
\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = "com.yukitakano.todonotes.TodoNotesWidget";
\t\t\t\tPRODUCT_NAME = "$(TARGET_NAME)";
\t\t\t\tSKIP_INSTALL = YES;
\t\t\t\tSWIFT_EMIT_LOC_STRINGS = YES;
\t\t\t\tSWIFT_VERSION = 5.0;
\t\t\t\tTARGETED_DEVICE_FAMILY = "1,2";
\t\t\t}};
\t\t\tname = {name};
\t\t}};'''

app_debug = app_config(ids["config_app_debug"], "Debug")
app_release = app_config(ids["config_app_release"], "Release")
widget_debug = widget_config(ids["config_widget_debug"], "Debug")
widget_release = widget_config(ids["config_widget_release"], "Release")

configlist_project = f'''\t\t{ids["configlist_project"]} /* Build configuration list for PBXProject "TodoNotes" */ = {{
\t\t\tisa = XCConfigurationList;
\t\t\tbuildConfigurations = (
\t\t\t\t{ids["config_project_debug"]} /* Debug */,
\t\t\t\t{ids["config_project_release"]} /* Release */,
\t\t\t);
\t\t\tdefaultConfigurationIsVisible = 0;
\t\t\tdefaultConfigurationName = Release;
\t\t}};'''

configlist_app = f'''\t\t{ids["configlist_app"]} /* Build configuration list for PBXNativeTarget "TodoNotes" */ = {{
\t\t\tisa = XCConfigurationList;
\t\t\tbuildConfigurations = (
\t\t\t\t{ids["config_app_debug"]} /* Debug */,
\t\t\t\t{ids["config_app_release"]} /* Release */,
\t\t\t);
\t\t\tdefaultConfigurationIsVisible = 0;
\t\t\tdefaultConfigurationName = Release;
\t\t}};'''

configlist_widget = f'''\t\t{ids["configlist_widget"]} /* Build configuration list for PBXNativeTarget "TodoNotesWidgetExtension" */ = {{
\t\t\tisa = XCConfigurationList;
\t\t\tbuildConfigurations = (
\t\t\t\t{ids["config_widget_debug"]} /* Debug */,
\t\t\t\t{ids["config_widget_release"]} /* Release */,
\t\t\t);
\t\t\tdefaultConfigurationIsVisible = 0;
\t\t\tdefaultConfigurationName = Release;
\t\t}};'''

# ---------------------------------------------------------------------
# Assemble
# ---------------------------------------------------------------------

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

out.append("\n/* Begin PBXContainerItemProxy section */")
out.append(container_item_proxy)
out.append("/* End PBXContainerItemProxy section */")

out.append("\n/* Begin PBXCopyFilesBuildPhase section */")
out.append(embed_widget_phase)
out.append("/* End PBXCopyFilesBuildPhase section */")

out.append("\n/* Begin PBXFileReference section */")
out.extend(fileref_lines)
out.append("/* End PBXFileReference section */")

out.append("\n/* Begin PBXFrameworksBuildPhase section */")
out.append(frameworks_phase_app)
out.append(frameworks_phase_widget)
out.append("/* End PBXFrameworksBuildPhase section */")

out.append("\n/* Begin PBXGroup section */")
out.append(group_lines)
out.append("/* End PBXGroup section */")

out.append("\n/* Begin PBXNativeTarget section */")
out.append(target_app)
out.append(target_widget)
out.append("/* End PBXNativeTarget section */")

out.append("\n/* Begin PBXProject section */")
out.append(project)
out.append("/* End PBXProject section */")

out.append("\n/* Begin PBXResourcesBuildPhase section */")
out.append(resources_phase_app)
out.append(resources_phase_widget)
out.append("/* End PBXResourcesBuildPhase section */")

out.append("\n/* Begin PBXSourcesBuildPhase section */")
out.append(sources_phase_app)
out.append(sources_phase_widget)
out.append("/* End PBXSourcesBuildPhase section */")

out.append("\n/* Begin PBXTargetDependency section */")
out.append(target_dependency)
out.append("/* End PBXTargetDependency section */")

out.append("\n/* Begin XCBuildConfiguration section */")
out.append(project_debug)
out.append(project_release)
out.append(app_debug)
out.append(app_release)
out.append(widget_debug)
out.append(widget_release)
out.append("/* End XCBuildConfiguration section */")

out.append("\n/* Begin XCConfigurationList section */")
out.append(configlist_project)
out.append(configlist_app)
out.append(configlist_widget)
out.append("/* End XCConfigurationList section */")

out.append("\t};")
out.append(f'\trootObject = {ids["project"]} /* Project object */;')
out.append("}")

text = "\n".join(out) + "\n"

with open("TodoNotes.xcodeproj/project.pbxproj", "w") as f:
    f.write(text)

print("Wrote TodoNotes.xcodeproj/project.pbxproj")
print("Total objects:", len(ids))
