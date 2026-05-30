use std::process::Command;
use std::time::Duration;
use std::env;

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        usage(1);
    }

    let s = "sliver";
    match args[1].as_str() {
        "beacons" | "b" => {
            clear(s);
            send(s, "beacons", 3);
            print_output(s, 40, "ID");
        }
        "use" => {
            if args.len() < 3 { usage(2); }
            clear(s);
            let cmd = format!("use {}", &args[2]);
            send(s, &cmd, 3);
            print_output(s, 15, "Active");
        }
        "task" | "exec" => {
            if args.len() < 3 { usage(3); }
            clear(s);
            let cmd = args[2..].join(" ");
            send(s, &cmd, 3);
            let out = capture(s, 30);
            for l in out.lines().rev().take(5) {
                if l.trim().contains("Tasked") {
                    println!("tasked: {}", l.trim());
                    break;
                }
            }
        }
        "wait" | "out" => {
            let secs: u64 = args.get(2).and_then(|v| v.parse().ok()).unwrap_or(90);
            wait(secs);
            let out = capture(s, 80);
            let lines: Vec<&str> = out.lines().collect();
            let start = lines.len().saturating_sub(60);
            for l in &lines[start..] {
                let t = l.trim();
                if t.is_empty() || has_spinner(t) || t.contains("Uploading") { continue; }
                println!("{}", t);
            }
        }
        "upload" | "up" => {
            if args.len() < 3 { usage(4); }
            clear(s);
            let cmd = format!("upload {}", &args[2..].join(" "));
            send(s, &cmd, 4);
            let out = capture(s, 25);
            for l in out.lines().rev().take(5) {
                if l.contains("Tasked") || l.contains("Upload") { println!("{}", l.trim()); }
            }
        }
        "kill" | "k" => {
            if args.len() < 3 { usage(5); }
            clear(s);
            send(s, &format!("beacons -k {}", &args[2]), 3);
            let out = capture(s, 20);
            for l in out.lines().rev().take(3) {
                if l.contains("Killed") { println!("{}", l.trim()); }
            }
        }
        "run" => {
            if args.len() < 5 { usage(6); }
            let beacon = &args[2];
            let cmd = &args[3..args.len()-1].join(" ");
            let wait_secs: u64 = args.last().unwrap().parse().unwrap_or(90);

            // Fresh prompt + select beacon + send command (NO Ctrl+C — kills Sliver TUI)
            send(s, "", 2);                         // Enter = fresh prompt
            send(s, &format!("use {}", beacon), 3);
            send(s, cmd, 3);

            println!("[run] {} > {} (wait {}s)", beacon, cmd, wait_secs);
            wait(wait_secs);

            let out = capture(s, 80);
            let lines: Vec<&str> = out.lines().collect();
            let start = lines.len().saturating_sub(60);
            for l in &lines[start..] {
                let t = l.trim();
                if t.is_empty() || has_spinner(t)
                    || t.contains("Uploading") || t.contains("/amd64")
                    || l.starts_with("  ") && l.len() > 2 && l[2..].starts_with(|c: char| c.is_ascii_hexdigit())
                { continue; }
                println!("{}", t);
            }
        }
        _ => {
            let cmd = args[1..].join(" ");
            send(s, &cmd, 3);
            print_output(s, 50, "");
        }
    }
}

// ─── helpers ───

fn usage(exit: i32) -> ! {
    eprintln!("c2 ─ sliver tmux helper\n");
    eprintln!("Usage:");
    eprintln!("  c2 beacons                 List beacons");
    eprintln!("  c2 use <id>                Select beacon");
    eprintln!("  c2 task <cmd...>           Queue beacon command");
    eprintln!("  c2 wait [secs]             Wait & show output");
    eprintln!("  c2 upload <src> [dst]      Upload file");
    eprintln!("  c2 kill <id>               Kill beacon");
    eprintln!("  c2 run <id> <cmd...> <wait> Full cycle: select + task + wait + output");
    std::process::exit(exit);
}

fn clear(session: &str) {
    // Only Enter — C-c kills the Sliver TUI client
    let _ = Command::new("tmux")
        .args(["send-keys", "-t", session, "Enter"])
        .output();
    wait(1);
}

fn send(session: &str, command: &str, sleep_secs: u64) {
    let _ = Command::new("tmux")
        .args(["send-keys", "-t", session, command, "Enter"])
        .output();
    wait(sleep_secs);
}

fn send_raw(session: &str, keys: &[&str]) {
    let mut args = vec!["send-keys", "-t", session];
    args.extend_from_slice(keys);
    let _ = Command::new("tmux").args(&args).output();
}

fn capture(session: &str, lines: usize) -> String {
    let arg = format!("-{}", lines);
    let o = Command::new("tmux")
        .args(["capture-pane", "-t", session, "-p", "-S", &arg])
        .output();
    match o {
        Ok(o) => strip_ansi(&String::from_utf8_lossy(&o.stdout)),
        Err(_) => String::new(),
    }
}

fn wait(secs: u64) {
    std::thread::sleep(Duration::from_secs(secs));
}

fn strip_ansi(input: &str) -> String {
    let mut out = String::with_capacity(input.len());
    let mut chars = input.chars();
    while let Some(c) = chars.next() {
        if c == '\x1b' {
            if chars.next() == Some('[') {
                for n in chars.by_ref() {
                    if !matches!(n, '0'..='9' | ';') { break; }
                }
            }
        } else if c != '\r' {
            out.push(c);
        }
    }
    out
}

fn has_spinner(s: &str) -> bool {
    s.contains('\u{280b}') || s.contains('\u{2809}') || s.contains('\u{2819}')
        || s.contains("⠋") || s.contains("⠙") || s.contains("⠹")
        || s.contains("⠸") || s.contains("⠼") || s.contains("⠴")
        || s.contains("⠦") || s.contains("⠧") || s.contains("⠇") || s.contains("⠏")
}

fn print_output(session: &str, lines: usize, filter: &str) {
    let out = capture(session, lines);
    let mut printing = filter.is_empty();
    for l in out.lines() {
        if !filter.is_empty() && l.contains(filter) { printing = true; }
        if printing {
            if l.trim().is_empty() { if !filter.is_empty() { break; } else { continue; } }
            println!("{}", l);
        }
    }
}
