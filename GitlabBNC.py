import datetime
import subprocess
import os
import re

# Gitlab Backup and Cleanup
# Author : Fatih Tuluk
# E-Mail : fatih4159@gmail.com
#Usage: sudo python3 GitlabBNC.py /var/opt/gitlab/backups/ /RemoteBackup/ 30
#       ad this script to your cronjobs and it will trigger creating a backup and deleting old backups which are older than the given days


# Writes log to a file
def log2file(text2log):
    log2file(text2log)
    # Create a log file if not already available
    log_file = "/tmp/gitlab-bnc-logs/gitlab-backup-" + datetime.datetime.today().strftime("%F") + ".log"
    if not os.path.exists(log_file):
        open(log_file, "w").close()

    # Write to the logfile
    with open(log_file, "a") as f:
        f.write("[" + datetime.datetime.today().strftime("%F %T") + "] " + text2log + "\n")

# Removes unused backup files
def remove_old_files(backup_directory, max_keep_days):
    today = datetime.datetime.today()
    thirty_days_ago = today - datetime.timedelta(days=int(max_keep_days))

    old_files = []
    for file in os.listdir(backup_directory):
        if file.endswith(".tar.gz"):
            file_path = os.path.join(backup_directory, file)
            file_date = datetime.date.fromtimestamp(os.path.getmtime(file_path))

            if file_date < thirty_days_ago:
                old_files.append(file)

    for file in old_files:
        if os.path.exists(file_path):
            os.remove(file_path)
            
def extract_date(filename):
    # Extract the date portion of the filename using regular expression
    match = re.search(r'(\d{4}_\d{2}_\d{2})', filename)
    if match:
        return match.group(1)
    else:
        return None

def main():
    # Get the backup directory, remote backup directory, and max keep days from the command line arguments
    import sys
    backup_directory = sys.argv[1]
    remote_backup_directory = sys.argv[2]
    max_keep_days = sys.argv[3]
    print("Starting Backup Process...")
    print("Backup-Directory is "+backup_directory)
    print("Remote Backup-Directory is "+remote_backup_directory)
    print("Maximum Days of keeping Backups is "+max_keep_days)

    # Get the current date
    today = datetime.datetime.today()
    print("The current Date is "+ str(today))

    log2file("cleaning up files in "+backup_directory+" older than "+max_keep_days)
    # Remove old files from the backup directory
    remove_old_files(backup_directory, max_keep_days)
    
    log2file("cleaning up files in "+remote_backup_directory+" older than "+max_keep_days)
    # Remove old files from the remote backup directory
    remove_old_files(remote_backup_directory, max_keep_days)
    log2file("Old-Files has been cleaned up")

    # Create a backup of the Gitlab repository
    log2file("Creating backup...")
    process = subprocess.run(["sudo", "gitlab-backup", "create"], check=True, capture_output=True)
    log2file(process.stdout.decode("utf-8"))

    # Get the newest file in the backups directory
    
    dirlist = os.listdir(backup_directory)
    
    log2file("Total backups <30 Days = "+str(len(dirlist)))
        
    
    log2file("Sorting the files list...")
    
    sortedlist = sorted(dirlist, key=lambda x: extract_date(x))

    
    for file in sortedlist:
        log2file(file)
    
    newest_file = sortedlist[-1]
    
    log2file("newest file is "+newest_file)
    
    # Copy the newest file to the RemoteBackup directory
    log2file("Copying backup to remote...")
    process =subprocess.run(["sudo", "cp", os.path.join(backup_directory, newest_file), remote_backup_directory], check=True, capture_output=True)
    log2file(process.stdout.decode("utf-8"))

    # Write a message to the log file
    log2file("Backup complete!")

if __name__ == "__main__":
    main()
