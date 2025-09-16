//! Memory monitoring module for real-time memory usage tracking

use sysinfo::{System, Pid};
use std::sync::{Arc, Mutex};
use std::time::Duration;
use tokio::time;
use tracing::debug;
use crate::{AppState, LogLevel};

/// Start memory monitoring in the background
pub async fn start_memory_monitoring(app_state: Arc<Mutex<AppState>>) {
    let mut system = System::new_all();
    let current_pid = Pid::from_u32(std::process::id());
    
    loop {
        // Check if memory monitoring is enabled
        let monitor_enabled = {
            let state = app_state.lock().unwrap();
            state.config.monitor_memory
        };
        
        if monitor_enabled {
            system.refresh_processes_specifics(sysinfo::ProcessesToUpdate::Some(&[current_pid]), sysinfo::ProcessRefreshKind::new());
            
            if let Some(process) = system.process(current_pid) {
                let memory_kb = process.memory();
                let memory_mb = memory_kb as f32 / 1024.0;
                
                debug!("Memory usage: {:.1} MB", memory_mb);
                
                // Update app state
                {
                    let mut state = app_state.lock().unwrap();
                    state.memory_usage_mb = memory_mb;
                    
                    // Log high memory usage
                    if memory_mb > 200.0 {
                        state.add_log_entry(
                            format!("High memory usage: {:.1} MB", memory_mb),
                            LogLevel::Warning,
                        );
                    }
                }
            } else {
                // Failed to get process info, use default value
                let mut state = app_state.lock().unwrap();
                state.memory_usage_mb = 0.0;
            }
        }
        
        // Update every 2 seconds
        time::sleep(Duration::from_secs(2)).await;
    }
}