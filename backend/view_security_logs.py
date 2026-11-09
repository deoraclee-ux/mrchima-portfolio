"""
Security Audit Log Viewer
View all download attempts and security violations
"""

import sqlite3
from datetime import datetime
from tabulate import tabulate

def view_tokens():
    """View all active download tokens"""
    print("\n" + "="*80)
    print("ACTIVE DOWNLOAD TOKENS")
    print("="*80 + "\n")
    
    conn = sqlite3.connect('secure_downloads.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT product_id, customer_email, customer_ip, downloads, max_downloads, 
               invalidated, created_at, expires_at
        FROM download_tokens
        ORDER BY created_at DESC
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print("No tokens found.\n")
        return
    
    headers = ['Product', 'Email', 'IP', 'Downloads', 'Max', 'Used', 'Created', 'Expires']
    table_data = []
    
    for row in rows:
        product, email, ip, downloads, max_downloads, invalidated, created, expires = row
        table_data.append([
            product,
            email[:30],
            ip,
            f"{downloads}/{max_downloads}",
            "✓" if max_downloads else "",
            "YES" if invalidated else "NO",
            created[:19],
            expires[:19]
        ])
    
    print(tabulate(table_data, headers=headers, tablefmt='grid'))
    print(f"\nTotal tokens: {len(rows)}\n")


def view_download_attempts():
    """View all download attempts (security audit log)"""
    print("\n" + "="*80)
    print("DOWNLOAD ATTEMPTS LOG (Last 50)")
    print("="*80 + "\n")
    
    conn = sqlite3.connect('secure_downloads.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT timestamp, token, ip_address, success, reason
        FROM download_attempts
        ORDER BY timestamp DESC
        LIMIT 50
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print("No download attempts logged yet.\n")
        return
    
    headers = ['Time', 'Token', 'IP', 'Status', 'Reason']
    table_data = []
    
    for row in rows:
        timestamp, token, ip, success, reason = row
        status = "✓ SUCCESS" if success else "✗ FAILED"
        table_data.append([
            timestamp[:19],
            token[:16] + "...",
            ip,
            status,
            reason[:40]
        ])
    
    print(tabulate(table_data, headers=headers, tablefmt='grid'))
    print(f"\nTotal attempts: {len(rows)}\n")


def view_security_violations():
    """View only failed attempts (security violations)"""
    print("\n" + "="*80)
    print("SECURITY VIOLATIONS (Failed Attempts Only)")
    print("="*80 + "\n")
    
    conn = sqlite3.connect('secure_downloads.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT timestamp, token, ip_address, user_agent, reason
        FROM download_attempts
        WHERE success = 0
        ORDER BY timestamp DESC
        LIMIT 30
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print("✓ No security violations! All download attempts were legitimate.\n")
        return
    
    headers = ['Time', 'Token', 'IP', 'Browser', 'Violation Reason']
    table_data = []
    
    for row in rows:
        timestamp, token, ip, user_agent, reason = row
        browser = user_agent[:40] if user_agent else "unknown"
        table_data.append([
            timestamp[:19],
            token[:12] + "...",
            ip,
            browser,
            reason
        ])
    
    print(tabulate(table_data, headers=headers, tablefmt='grid'))
    print(f"\n⚠️  Total violations: {len(rows)}\n")


def view_stats():
    """View security statistics"""
    print("\n" + "="*80)
    print("SECURITY STATISTICS")
    print("="*80 + "\n")
    
    conn = sqlite3.connect('secure_downloads.db')
    cursor = conn.cursor()
    
    # Total tokens
    cursor.execute('SELECT COUNT(*) FROM download_tokens')
    total_tokens = cursor.fetchone()[0]
    
    # Active tokens (not invalidated, not expired)
    cursor.execute('''
        SELECT COUNT(*) FROM download_tokens 
        WHERE invalidated = 0 AND expires_at > ?
    ''', (datetime.now().isoformat(),))
    active_tokens = cursor.fetchone()[0]
    
    # Total downloads
    cursor.execute('SELECT SUM(downloads) FROM download_tokens')
    total_downloads = cursor.fetchone()[0] or 0
    
    # Successful attempts
    cursor.execute('SELECT COUNT(*) FROM download_attempts WHERE success = 1')
    successful = cursor.fetchone()[0]
    
    # Failed attempts
    cursor.execute('SELECT COUNT(*) FROM download_attempts WHERE success = 0')
    failed = cursor.fetchone()[0]
    
    # Most common violation
    cursor.execute('''
        SELECT reason, COUNT(*) as count 
        FROM download_attempts 
        WHERE success = 0 
        GROUP BY reason 
        ORDER BY count DESC 
        LIMIT 1
    ''')
    top_violation = cursor.fetchone()
    
    conn.close()
    
    print(f"📊 Total Tokens Generated: {total_tokens}")
    print(f"✓ Active Tokens: {active_tokens}")
    print(f"📥 Total Successful Downloads: {total_downloads}")
    print(f"✓ Successful Attempts: {successful}")
    print(f"✗ Failed Attempts: {failed}")
    
    if total_downloads > 0:
        success_rate = (successful / (successful + failed)) * 100 if (successful + failed) > 0 else 0
        print(f"🎯 Success Rate: {success_rate:.1f}%")
    
    if top_violation:
        print(f"⚠️  Most Common Violation: {top_violation[0]} ({top_violation[1]} times)")
    
    print()


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("\n🔒 Security Audit Log Viewer\n")
        print("Usage:")
        print("  python view_security_logs.py tokens       - View all download tokens")
        print("  python view_security_logs.py attempts     - View all download attempts")
        print("  python view_security_logs.py violations   - View security violations only")
        print("  python view_security_logs.py stats        - View security statistics")
        print()
        sys.exit(0)
    
    command = sys.argv[1].lower()
    
    try:
        if command == 'tokens':
            view_tokens()
        elif command == 'attempts':
            view_download_attempts()
        elif command == 'violations':
            view_security_violations()
        elif command == 'stats':
            view_stats()
        else:
            print(f"Unknown command: {command}")
            print("Use: tokens, attempts, violations, or stats")
    except sqlite3.OperationalError as e:
        print(f"Error: {e}")
        print("\nDatabase not found or not initialized.")
        print("Start the backend server first to create the database.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
