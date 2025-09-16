//! File output and monitoring module

use anyhow::Result;
use notify::{Watcher, RecursiveMode, Event, EventKind, RecommendedWatcher};
use std::path::Path;
use std::sync::{Arc, Mutex, mpsc};
use tracing::{info, error, debug};
use crate::{AppState, LogLevel};

/// Start file monitoring for text.txt changes
pub async fn start_file_monitoring(app_state: Arc<Mutex<AppState>>) -> Result<()> {
    info!("Starting file monitoring for text.txt");
    
    let (tx, rx) = mpsc::channel();
    
    let mut watcher: RecommendedWatcher = Watcher::new(
        move |result: notify::Result<Event>| {
            if let Err(e) = tx.send(result) {
                error!("Failed to send file event: {}", e);
            }
        },
        notify::Config::default(),
    )?;
    
    // Watch the current directory for text.txt changes
    let watch_path = Path::new(".");
    watcher.watch(watch_path, RecursiveMode::NonRecursive)?;
    
    info!("File watcher started for directory: {}", watch_path.display());
    
    // Process file events in a separate thread
    let app_state_clone = app_state.clone();
    std::thread::spawn(move || {
        loop {
            match rx.recv() {
                Ok(Ok(event)) => {
                    handle_file_event(event, &app_state_clone);
                }
                Ok(Err(e)) => {
                    error!("File watcher error: {}", e);
                    let mut state = app_state_clone.lock().unwrap();
                    state.add_log_entry(
                        format!("File watcher error: {}", e),
                        LogLevel::Error,
                    );
                }
                Err(e) => {
                    error!("File watcher channel error: {}", e);
                    break;
                }
            }
        }
    });
    
    // Keep watcher alive by moving it to a long-lived task
    tokio::spawn(async move {
        let _watcher = watcher; // Keep watcher alive
        
        // Sleep indefinitely to keep the watcher alive
        loop {
            tokio::time::sleep(std::time::Duration::from_secs(60)).await;
        }
    });
    
    Ok(())
}

fn handle_file_event(event: Event, app_state: &Arc<Mutex<AppState>>) {
    debug!("File event: {:?}", event);
    
    // Check if it's a write event on text.txt
    if let EventKind::Modify(_) = event.kind {
        for path in event.paths {
            if let Some(filename) = path.file_name() {
                if filename == "text.txt" {
                    debug!("text.txt was modified");
                    
                    // Read the file content
                    match std::fs::read_to_string(&path) {
                        Ok(content) => {
                            let content = content.trim();
                            if !content.is_empty() {
                                let mut state = app_state.lock().unwrap();
                                state.add_log_entry(
                                    format!("File updated: {}", content),
                                    LogLevel::Info,
                                );
                            }
                        }
                        Err(e) => {
                            error!("Failed to read text.txt: {}", e);
                            let mut state = app_state.lock().unwrap();
                            state.add_log_entry(
                                format!("Failed to read text.txt: {}", e),
                                LogLevel::Error,
                            );
                        }
                    }
                    break;
                }
            }
        }
    }
}