"""
PolicyKit integration for GUP Update Manager
"""

import subprocess
import os
import tempfile
from pathlib import Path
from utils.logger import Logger

class PolicyKitManager:
    """Manager for PolicyKit/pkexec operations"""
    
    def __init__(self):
        self.logger = Logger()
        self.policy_file = "/usr/share/polkit-1/actions/org.guideos.guideos-updater.policy"
        
    def is_pkexec_available(self):
        """Check if pkexec is available"""
        try:
            subprocess.run(['which', 'pkexec'], capture_output=True, check=True)
            return True
        except:
            return False
    
    def create_policy_file_content(self):
        """Generate PolicyKit policy file content"""
        return """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE policyconfig PUBLIC
 "-//freedesktop//DTD PolicyKit Policy Configuration 1.0//EN"
 "http://www.freedesktop.org/standards/PolicyKit/1/policyconfig.dtd">
<policyconfig>

  <vendor>GuideOS</vendor>
  <vendor_url>https://github.com/guideos/gup</vendor_url>

  <action id="org.guideos.guideos-updater.update-cache">
    <description>Update package cache</description>
    <message>Authentication required to update package cache</message>
    <icon_name>system-software-update</icon_name>
    <defaults>
      <allow_any>no</allow_any>
      <allow_inactive>no</allow_inactive>
      <allow_active>yes</allow_active>
    </defaults>
    <annotate key="org.freedesktop.policykit.exec.path">/usr/bin/apt</annotate>
    <annotate key="org.freedesktop.policykit.exec.allow_gui">true</annotate>
  </action>

  <action id="org.guideos.guideos-updater.install-packages">
    <description>Install or upgrade packages</description>
    <message>Authentication required to install or upgrade packages</message>
    <icon_name>system-software-update</icon_name>
    <defaults>
      <allow_any>no</allow_any>
      <allow_inactive>no</allow_inactive>
      <allow_active>auth_admin_keep</allow_active>
    </defaults>
    <annotate key="org.freedesktop.policykit.exec.path">/usr/bin/apt</annotate>
    <annotate key="org.freedesktop.policykit.exec.allow_gui">true</annotate>
  </action>

</policyconfig>"""

    def setup_policy(self):
        """Setup PolicyKit policy (requires manual installation)"""
        policy_content = self.create_policy_file_content()
        
        # Save policy to local directory for manual installation
        local_policy_dir = Path.home() / '.local' / 'share' / 'gup'
        local_policy_dir.mkdir(parents=True, exist_ok=True)
        
        local_policy_file = local_policy_dir / 'org.guideos.guideos-updater.policy'
        with open(local_policy_file, 'w') as f:
            f.write(policy_content)
        
        self.logger.info(f"PolicyKit policy saved to: {local_policy_file}")
        return str(local_policy_file)
    
    def run_with_pkexec(self, action_id, command):
        """Run command with pkexec"""
        try:
            if not self.is_pkexec_available():
                raise Exception("pkexec not available")
            
            # Check if policy is installed
            policy_file = f"/usr/share/polkit-1/actions/{action_id}.policy"
            if not os.path.exists(policy_file):
                raise Exception(f"PolicyKit policy not installed: {policy_file}")
            
            # Use pkexec without --action-id for now (simpler approach)
            cmd = ['pkexec'] + command
            
            result = subprocess.run(cmd, 
                                  capture_output=True, 
                                  text=True,
                                  timeout=300)  # 5 minute timeout
            
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            self.logger.error("Command timed out")
            return False, "Command timed out"
        except Exception as e:
            self.logger.error(f"Error running pkexec command: {e}")
            return False, str(e)
    
    def update_package_cache(self):
        """Update APT package cache using PolicyKit"""
        try:
            # Simple pkexec without action-id for broader compatibility
            cmd = ['pkexec', 'apt', 'update']
            result = subprocess.run(cmd, 
                                  capture_output=True, 
                                  text=True,
                                  timeout=300)
            
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr
        except Exception as e:
            return False, str(e)
    
    def install_packages(self, packages):
        """Install packages using PolicyKit"""
        try:
            # Simple pkexec without action-id for broader compatibility
            cmd = ['pkexec', 'apt', 'install', '-y'] + packages
            result = subprocess.run(cmd,
                                  capture_output=True, 
                                  text=True,
                                  timeout=300)
            
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr
        except Exception as e:
            return False, str(e)