"""
Copyright 2025 Amazon.com, Inc. or its affiliates.  All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
# Import required libraries for file system operations
import os
import shutil
from pathlib import Path
from strands import tool

# Strands tool decorator for file organization functionality
# This function serves as a Strands Agents tool that automatically organizes files in a directory by their type. It creates categorized folders and moves files accordingly while providing detailed operation summaries.
@tool
def file_organizer(source_directory: str, organize_by_type: bool = True) -> str:
    """
    Organize files in a directory by type, creating folders and moving files accordingly.
    Cross-platform compatible (Windows, Linux, macOS).
    
    Args:
        source_directory: Path to the directory containing files to organize
        organize_by_type: If True, organize by file type categories
    
    Returns:
        Summary of organization results
    """
    
    # File categorization mapping dictionary
    # This dictionary defines how files are categorized based on their extensions, supporting common document types, media files, archives, and executables. It ensures cross-platform compatibility by including extensions from Windows, macOS, and Linux systems.
    file_categories = {
        'Word Documents': ['.doc', '.docx', '.rtf', '.odt'],
        'Excel Documents': ['.xls', '.xlsx', '.csv', '.ods'],
        'PowerPoint Documents': ['.ppt', '.pptx', '.odp'],
        'PDF Documents': ['.pdf'],
        'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp'],
        'Videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
        'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma'],
        'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
        'Text Files': ['.txt', '.md', '.log'],
        'Code Files': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.php'],
        'Executables': ['.exe', '.msi', '.bat', '.cmd', '.sh', '.run', '.deb', '.rpm', '.appimage']
    }
    
    # Directory validation and initialization
    # This section validates the input directory path and initializes tracking variables for the organization process. It ensures the directory exists and is accessible before proceeding with file operations.
    try:
        source_path = Path(source_directory)
        if not source_path.exists():
            return f"Error: Directory '{source_directory}' does not exist"
        
        if not source_path.is_dir():
            return f"Error: '{source_directory}' is not a directory"
        
        organized_count = 0
        created_folders = set()
        file_moves = []  # Track file movements
        
        # File discovery and state recording
        # This section scans the directory for files and records the initial state before organization. It filters out subdirectories and creates a snapshot of all files that will be processed.
        files = [f for f in source_path.iterdir() if f.is_file()]
        
        if not files:
            return f"No files found in '{source_directory}'"
        
        # Record before state
        before_state = [f.name for f in files]
        
        # File categorization and folder assignment
        # This loop processes each file by examining its extension and matching it to the appropriate category. Files that don't match any predefined category are placed in an 'Other Files' folder to ensure all files are organized.
        for file_path in files:
            file_extension = file_path.suffix.lower()
            
            # Find the appropriate category
            target_folder = None
            for category, extensions in file_categories.items():
                if file_extension in extensions:
                    target_folder = category
                    break
            
            # If no category found, use 'Other Files'
            if not target_folder:
                target_folder = 'Other Files'
            
            # Directory creation and file movement
            # This section creates the target category folders if they don't exist and handles the actual file movement. It includes duplicate name resolution by appending numbers to ensure no files are overwritten during the organization process.
            target_dir = source_path / target_folder
            if not target_dir.exists():
                target_dir.mkdir(exist_ok=True)
                created_folders.add(target_folder)
            
            # Move the file
            target_file_path = target_dir / file_path.name
            
            # Handle duplicate names
            counter = 1
            original_name = file_path.stem
            extension = file_path.suffix
            
            while target_file_path.exists():
                new_name = f"{original_name}_{counter}{extension}"
                target_file_path = target_dir / new_name
                counter += 1
            
            shutil.move(str(file_path), str(target_file_path))
            organized_count += 1
            
            # Record the move
            file_moves.append({
                'file': file_path.name,
                'from': 'Root Directory',
                'to': target_folder,
                'new_name': target_file_path.name
            })
        
        # Comprehensive operation summary generation
        # This section creates a detailed report of the organization process, showing before/after states, file movements, and folder creation. It provides users with complete visibility into what changes were made during the organization operation.
        summary = f"✅ File organization complete!\n\n"
        
        # Before state
        summary += f"📋 BEFORE: {len(before_state)} files in root directory\n"
        summary += f"Files: {', '.join(before_state[:5])}{'...' if len(before_state) > 5 else ''}\n\n"
        
        # Changes made
        summary += f"🔄 CHANGES MADE:\n"
        for move in file_moves:
            if move['file'] != move['new_name']:
                summary += f"• {move['file']} → {move['to']}/{move['new_name']} (renamed)\n"
            else:
                summary += f"• {move['file']} → {move['to']}/\n"
        
        # After state
        summary += f"\n📂 AFTER: Created {len(created_folders)} folders\n"
        for folder in sorted(created_folders):
            folder_files = [m['new_name'] for m in file_moves if m['to'] == folder]
            summary += f"• {folder}: {len(folder_files)} files\n"
        
        summary += f"\n📍 Location: {source_directory}"
        
        return summary
        
    # Error handling for common file operation issues
    # This section catches and handles permission errors and other exceptions that may occur during file operations. It provides user-friendly error messages with actionable guidance for resolving common issues.
    except PermissionError:
        return f"❌ Error: Permission denied. Run as administrator or check file permissions."
    except Exception as e:
        return f"❌ Error organizing files: {str(e)}"