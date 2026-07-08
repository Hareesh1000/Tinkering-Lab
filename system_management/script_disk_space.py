import subprocess
import oracledb


def get_disk_space():
    """
    Executes PowerShell command to fetch disk space details.
    """
    print("INFO: Fetching disk space information...")

    command = (
        'powershell "Get-WmiObject Win32_LogicalDisk | '
        'Select-Object DeviceID,'
        '@{Name=\'FreeSpaceMB\';Expression={[math]::Round($_.FreeSpace/1MB,2)}},'
        '@{Name=\'SizeMB\';Expression={[math]::Round($_.Size/1MB,2)}}"'
    )

    result = subprocess.run(command, capture_output=True, text=True)

    output = result.stdout.splitlines()

    # Skip header
    return output[3:]


def log_error(cursor, conn, message):
    """
    Insert error log into logger table
    """
    cursor.execute("""
        INSERT INTO app_logger
        (log_id, log_level, module_name, log_message)
        VALUES (seq_app_logger_id.NEXTVAL, 'ERROR', 'DISK_MONITOR', :1)
    """, (message,))

    conn.commit()


def insert_disk_data(cursor, conn, data_lines):
    """
    Insert disk details into database
    """

    for line in data_lines:

        line = line.strip()

        if not line:
            continue

        parts = line.split()

        if len(parts) < 3:
            continue

        device = parts[0]
        free_mb = parts[1]
        size_mb = parts[2]

        try:

            cursor.execute("""
                INSERT INTO system_disk_audit
                (sno, deviceid, freespace_mb, size_mb)
                VALUES (seq_system_disk_audit_sno.NEXTVAL, :1, :2, :3)
            """, (device, free_mb, size_mb))

            print(f"INFO: Inserted disk data for {device}")

        except Exception as e:

            error_msg = f"Error inserting disk data for {device}: {str(e)}"
            print("ERROR:", error_msg)

            log_error(cursor, conn, error_msg)


def main():

    conn = None
    cursor = None

    try:

        # Get disk data
        data_lines = get_disk_space()

        print("INFO: Connecting to Oracle database...")

        conn = oracledb.connect(
            user="developer",
            password="developer",
            dsn="localhost/orclpdb"
        )

        cursor = conn.cursor()

        print("INFO: Connected successfully")

        insert_disk_data(cursor, conn, data_lines)

        conn.commit()

        print("INFO: Disk data inserted successfully")

    except Exception as e:

        print("ERROR:", str(e))

        if cursor and conn:
            log_error(cursor, conn, str(e))

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

        print("INFO: Database connection closed")


if __name__ == "__main__":
    main()