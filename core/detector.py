import json
from pathlib import Path
from utils.logger import logger

def detect_project_info(node_modules_path: str):
    """
    Given the path to a node_modules folder, analyze the parent directory
    to extract lightweight project info.
    """
    nm_path = Path(node_modules_path)
    parent_path = nm_path.parent

    info = {
        "project_name": parent_path.name,
        "framework": "Unknown",
        "package_manager": "Unknown",
        "has_git": False,
        "last_modified": 0.0
    }

    try:
        info["last_modified"] = nm_path.stat().st_mtime
    except Exception as e:
        logger.debug(f"Could not read stat for {nm_path}: {e}")

    # Check Git
    git_path = parent_path / ".git"
    if git_path.exists():
        info["has_git"] = True

    # Check Package Manager
    if (parent_path / "yarn.lock").exists():
        info["package_manager"] = "Yarn"
    elif (parent_path / "pnpm-lock.yaml").exists():
        info["package_manager"] = "pnpm"
    elif (parent_path / "bun.lockb").exists():
        info["package_manager"] = "Bun"
    elif (parent_path / "package-lock.json").exists():
        info["package_manager"] = "npm"
    else:
        info["package_manager"] = "npm (assumed)"

    # Check Framework via package.json
    pkg_json = parent_path / "package.json"
    if pkg_json.exists():
        try:
            with open(pkg_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Check dependencies and devDependencies
                deps = data.get("dependencies", {})
                dev_deps = data.get("devDependencies", {})
                all_deps = {**deps, **dev_deps}
                
                # Simple framework heuristic
                if "next" in all_deps:
                    info["framework"] = "Next.js"
                elif "nuxt" in all_deps:
                    info["framework"] = "Nuxt.js"
                elif "react" in all_deps and "react-scripts" in all_deps:
                    info["framework"] = "React (CRA)"
                elif "react" in all_deps and "vite" in all_deps:
                    info["framework"] = "React (Vite)"
                elif "vue" in all_deps:
                    if "vite" in all_deps:
                        info["framework"] = "Vue (Vite)"
                    else:
                        info["framework"] = "Vue"
                elif "@angular/core" in all_deps:
                    info["framework"] = "Angular"
                elif "svelte" in all_deps:
                    info["framework"] = "Svelte"
                elif "express" in all_deps:
                    info["framework"] = "Express"
                elif "electron" in all_deps:
                    info["framework"] = "Electron"
                elif "react-native" in all_deps:
                    info["framework"] = "React Native"
                else:
                    info["framework"] = "Node.js (Generic)"
                    
        except Exception as e:
            logger.debug(f"Failed to parse package.json for {parent_path}: {e}")
            
    return info

def calculate_status(last_modified: float, has_git: bool) -> str:
    """Calculate project status based on last modification and git presence."""
    from utils.helpers import get_days_since
    days = get_days_since(last_modified)
    
    if days < 30:
        return "🟢 Active"
    elif days < 180:
        return "🟡 Recently Modified"
    else:
        return "🔴 Old Project"
