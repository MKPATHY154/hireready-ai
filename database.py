"""
Database module for HireReady AI.
SQLite-based persistence for sessions, skill gaps, roadmaps, and progress tracking.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), "hireready.db")


@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """Initialize database tables."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Sessions table - stores resume + job description pairs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_text TEXT NOT NULL,
                resume_skills TEXT NOT NULL,  -- JSON array
                job_description TEXT NOT NULL,
                job_required_skills TEXT,     -- JSON array
                job_preferred_skills TEXT,    -- JSON array
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Skill gaps table - stores gap analysis results
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skill_gaps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                matched_skills TEXT NOT NULL,         -- JSON array
                missing_critical TEXT NOT NULL,       -- JSON array
                missing_preferred TEXT NOT NULL,      -- JSON array
                gap_summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
            )
        """)

        # Roadmaps table - stores generated learning roadmaps
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS roadmaps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                roadmap_data TEXT NOT NULL,           -- JSON object with weeks, tasks, resources
                total_weeks INTEGER DEFAULT 10,
                estimated_hours_per_week INTEGER DEFAULT 8,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
            )
        """)

        # Roadmap tasks table - individual tasks with completion status
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS roadmap_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                roadmap_id INTEGER NOT NULL,
                week_number INTEGER NOT NULL,
                task_index INTEGER NOT NULL,
                task_description TEXT NOT NULL,
                skill_focus TEXT,                     -- JSON array of skills
                resource_urls TEXT,                   -- JSON array of resource objects
                is_completed BOOLEAN DEFAULT FALSE,
                completed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (roadmap_id) REFERENCES roadmaps (id) ON DELETE CASCADE
            )
        """)

        # Progress table - aggregated progress tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                roadmap_id INTEGER NOT NULL,
                total_tasks INTEGER DEFAULT 0,
                completed_tasks INTEGER DEFAULT 0,
                current_week INTEGER DEFAULT 1,
                streak_days INTEGER DEFAULT 0,
                last_activity_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE,
                FOREIGN KEY (roadmap_id) REFERENCES roadmaps (id) ON DELETE CASCADE
            )
        """)

        # Create indexes for better query performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_created ON sessions(created_at DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_skill_gaps_session ON skill_gaps(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_roadmaps_session ON roadmaps(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_roadmap ON roadmap_tasks(roadmap_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_progress_session ON progress(session_id)")

        conn.commit()


# ==================== Session Operations ====================

def create_session(resume_text: str, resume_skills: List[str], job_description: str,
                   job_required_skills: List[str] = None, job_preferred_skills: List[str] = None) -> int:
    """Create a new session and return its ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sessions (resume_text, resume_skills, job_description, job_required_skills, job_preferred_skills)
            VALUES (?, ?, ?, ?, ?)
        """, (
            resume_text,
            json.dumps(resume_skills),
            job_description,
            json.dumps(job_required_skills or []),
            json.dumps(job_preferred_skills or [])
        ))
        conn.commit()
        return cursor.lastrowid


def get_session(session_id: int) -> Optional[Dict[str, Any]]:
    """Get session by ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def get_latest_session() -> Optional[Dict[str, Any]]:
    """Get the most recent session."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions ORDER BY created_at DESC LIMIT 1")
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def get_all_sessions(limit: int = 50) -> List[Dict[str, Any]]:
    """Get all sessions, most recent first."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions ORDER BY created_at DESC LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()]


# ==================== Skill Gap Operations ====================

def save_skill_gap(session_id: int, matched_skills: List[str], missing_critical: List[str],
                   missing_preferred: List[str], gap_summary: str) -> int:
    """Save skill gap analysis."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO skill_gaps (session_id, matched_skills, missing_critical, missing_preferred, gap_summary)
            VALUES (?, ?, ?, ?, ?)
        """, (
            session_id,
            json.dumps(matched_skills),
            json.dumps(missing_critical),
            json.dumps(missing_preferred),
            gap_summary
        ))
        conn.commit()
        return cursor.lastrowid


def get_skill_gap(session_id: int) -> Optional[Dict[str, Any]]:
    """Get skill gap for a session."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM skill_gaps WHERE session_id = ? ORDER BY created_at DESC LIMIT 1", (session_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


# ==================== Roadmap Operations ====================

def save_roadmap(session_id: int, roadmap_data: Dict[str, Any],
                 total_weeks: int = 10, estimated_hours_per_week: int = 8) -> int:
    """Save generated roadmap."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO roadmaps (session_id, roadmap_data, total_weeks, estimated_hours_per_week)
            VALUES (?, ?, ?, ?)
        """, (
            session_id,
            json.dumps(roadmap_data),
            total_weeks,
            estimated_hours_per_week
        ))
        roadmap_id = cursor.lastrowid

        # Also save individual tasks
        weeks = roadmap_data.get("weeks", [])
        for week in weeks:
            week_num = week.get("week", 0)
            tasks = week.get("tasks", [])
            skills = week.get("skills", [])
            resources = week.get("resources", [])
            for idx, task in enumerate(tasks):
                cursor.execute("""
                    INSERT INTO roadmap_tasks (roadmap_id, week_number, task_index, task_description, skill_focus, resource_urls)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    roadmap_id,
                    week_num,
                    idx,
                    task,
                    json.dumps(skills),
                    json.dumps(resources)
                ))

        conn.commit()
        return roadmap_id


def get_roadmap(roadmap_id: int) -> Optional[Dict[str, Any]]:
    """Get roadmap by ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM roadmaps WHERE id = ?", (roadmap_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def get_roadmap_by_session(session_id: int) -> Optional[Dict[str, Any]]:
    """Get latest roadmap for a session."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM roadmaps WHERE session_id = ? ORDER BY created_at DESC LIMIT 1", (session_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def get_roadmap_tasks(roadmap_id: int) -> List[Dict[str, Any]]:
    """Get all tasks for a roadmap."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM roadmap_tasks WHERE roadmap_id = ? ORDER BY week_number, task_index
        """, (roadmap_id,))
        return [dict(row) for row in cursor.fetchall()]


def update_task_completion(task_id: int, completed: bool) -> bool:
    """Update task completion status."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if completed:
            cursor.execute("""
                UPDATE roadmap_tasks SET is_completed = TRUE, completed_at = CURRENT_TIMESTAMP WHERE id = ?
            """, (task_id,))
        else:
            cursor.execute("""
                UPDATE roadmap_tasks SET is_completed = FALSE, completed_at = NULL WHERE id = ?
            """, (task_id,))
        conn.commit()
        return cursor.rowcount > 0


def get_task_completion_stats(roadmap_id: int) -> Dict[str, int]:
    """Get completion statistics for a roadmap."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN is_completed THEN 1 ELSE 0 END) as completed
            FROM roadmap_tasks WHERE roadmap_id = ?
        """, (roadmap_id,))
        row = cursor.fetchone()
        return {"total": row["total"] or 0, "completed": row["completed"] or 0}


# ==================== Progress Operations ====================

def init_progress(session_id: int, roadmap_id: int) -> int:
    """Initialize progress tracking for a roadmap."""
    stats = get_task_completion_stats(roadmap_id)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO progress (session_id, roadmap_id, total_tasks, completed_tasks, current_week, streak_days, last_activity_date)
            VALUES (?, ?, ?, ?, 1, 0, DATE('now'))
        """, (session_id, roadmap_id, stats["total"], stats["completed"]))
        conn.commit()
        return cursor.lastrowid


def get_progress(session_id: int) -> Optional[Dict[str, Any]]:
    """Get progress for a session."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM progress WHERE session_id = ? ORDER BY updated_at DESC LIMIT 1", (session_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def update_progress_on_task_complete(session_id: int, roadmap_id: int, week_number: int):
    """Update progress when a task is completed."""
    stats = get_task_completion_stats(roadmap_id)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Get current progress
        cursor.execute("SELECT * FROM progress WHERE session_id = ? AND roadmap_id = ?", (session_id, roadmap_id))
        row = cursor.fetchone()

        if row:
            # Calculate streak
            last_date = row["last_activity_date"]
            today = datetime.now().date()
            streak = row["streak_days"]
            if last_date:
                last = datetime.strptime(last_date, "%Y-%m-%d").date()
                if (today - last).days == 1:
                    streak += 1
                elif (today - last).days > 1:
                    streak = 1

            cursor.execute("""
                UPDATE progress SET 
                    completed_tasks = ?, 
                    current_week = ?,
                    streak_days = ?,
                    last_activity_date = DATE('now'),
                    updated_at = CURRENT_TIMESTAMP
                WHERE session_id = ? AND roadmap_id = ?
            """, (stats["completed"], week_number, streak, session_id, roadmap_id))
        else:
            cursor.execute("""
                INSERT INTO progress (session_id, roadmap_id, total_tasks, completed_tasks, current_week, streak_days, last_activity_date)
                VALUES (?, ?, ?, ?, ?, 1, DATE('now'))
            """, (session_id, roadmap_id, stats["total"], stats["completed"], week_number))
        conn.commit()


def get_weekly_progress(roadmap_id: int) -> List[Dict[str, Any]]:
    """Get progress breakdown by week."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                week_number,
                COUNT(*) as total_tasks,
                SUM(CASE WHEN is_completed THEN 1 ELSE 0 END) as completed_tasks
            FROM roadmap_tasks WHERE roadmap_id = ?
            GROUP BY week_number
            ORDER BY week_number
        """, (roadmap_id,))
        return [dict(row) for row in cursor.fetchall()]


# ==================== Utility Functions ====================

def parse_json_field(data: Dict, field: str, default=None):
    """Safely parse JSON field from database row."""
    if data and field in data and data[field]:
        try:
            return json.loads(data[field])
        except (json.JSONDecodeError, TypeError):
            return default or []
    return default or []


def session_to_dict(session: Dict) -> Dict:
    """Convert session row to dict with parsed JSON fields."""
    if not session:
        return {}
    return {
        **session,
        "resume_skills": parse_json_field(session, "resume_skills"),
        "job_required_skills": parse_json_field(session, "job_required_skills"),
        "job_preferred_skills": parse_json_field(session, "job_preferred_skills"),
    }


def skill_gap_to_dict(gap: Dict) -> Dict:
    """Convert skill gap row to dict with parsed JSON fields."""
    if not gap:
        return {}
    return {
        **gap,
        "matched_skills": parse_json_field(gap, "matched_skills"),
        "missing_critical": parse_json_field(gap, "missing_critical"),
        "missing_preferred": parse_json_field(gap, "missing_preferred"),
    }


def roadmap_to_dict(roadmap: Dict) -> Dict:
    """Convert roadmap row to dict with parsed JSON fields."""
    if not roadmap:
        return {}
    data = parse_json_field(roadmap, "roadmap_data", {})
    return {
        **roadmap,
        "roadmap_data": data,
        "weeks": data.get("weeks", []),
    }


# Initialize database on import
init_db()