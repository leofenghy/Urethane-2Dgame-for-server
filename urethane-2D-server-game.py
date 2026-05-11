#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════╗
║       URETHANE — 无限迷宫  Infinite Maze             ║
╠══════════════════════════════════════════════════════╣
║  安装依赖:  pip3 install flask                       ║
║  启动服务:  python3 weave_game.py                    ║
║  访问地址:  http://<IP>:8080                         ║
╚══════════════════════════════════════════════════════╝
"""
from flask import Flask
app = Flask(__name__)

GAME_HTML = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>URETHANE — 无限迷宫</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{
    font-family:'Courier New',Courier,monospace;
    background:#0d0d0d;color:#bbb;min-height:100vh;
    display:flex;flex-direction:column;align-items:center;
    overflow:hidden;user-select:none;
  }
  .topbar{
    width:100%;display:flex;align-items:center;
    padding:10px 20px;background:#111;
    border-bottom:1px solid #1a1a1a;gap:16px;
  }
  .logo{font-size:15px;font-weight:bold;color:#0f0;letter-spacing:4px;flex-shrink:0}
  .logo:hover{color:#fff;text-shadow:0 0 10px #00ff00}
  .page-id{font-size:13px;color:#777}
  .topbar-right{margin-left:auto;display:flex;gap:8px;align-items:center;font-size:12px;color:#555;letter-spacing:1px}
  .status-dot{display:inline-block;width:6px;height:6px;border-radius:50%;background:#00ff00;box-shadow:0 0 6px #00ff00;margin-right:6px}
  #wrap{display:flex;align-items:center;justify-content:center;flex:1;padding:12px 0 6px}
  canvas{display:block}
  .footer{width:100%;padding:8px 20px;border-top:1px solid #1a1a1a;display:flex;justify-content:space-between;font-size:11px;color:#444;letter-spacing:1px}
</style>
</head>
<body>
<div class="topbar">
  <span class="logo">URETHANE</span>
  <span class="page-id">/ INFINITE MAZE</span>
  <span class="topbar-right"><span class="status-dot"></span>RUNNING</span>
</div>
<div id="wrap"><canvas id="cv"></canvas></div>
<div class="footer">
  <span>↑ ↓ ← → NAVIGATE  ·  STAND STILL = IGNORE MONSTERS  ·  SURVIVE LONG ENOUGH = TROPHY SPAWNS</span>
  <span>SPACE / ENTER = START · RESTART</span>
</div>
<script>
/* ═══════════════════════════════════════════════════════
   CONSTANTS
═══════════════════════════════════════════════════════ */
const W=560, H=480;
const TILE=32, COLS=17, ROWS=13;
const GX=8,  GY=52;
const PCOL=3;
const MF="'Courier New',Courier,monospace";
let difficulty = 2;       // 1=easy(3min) 2=medium(5min) 3=hard(10min)
let WIN_TIME   = 300;   // seconds — updated when difficulty changes

/* ═══════════════════════════════════════════════════════
   CANVAS
═══════════════════════════════════════════════════════ */
const cv  = document.getElementById('cv');
const ctx = cv.getContext('2d');
const DPR = Math.min(window.devicePixelRatio||1, 2);
cv.width  = W*DPR; cv.height = H*DPR;
cv.style.width = W+'px'; cv.style.height = H+'px';
ctx.scale(DPR, DPR);

/* ═══════════════════════════════════════════════════════
   MAZE  — guaranteed solvable path via pathRow spine
   maze[wc]    = Array(ROWS) filled 0|1
   pathRow[wc] = the row guaranteed open for column wc
═══════════════════════════════════════════════════════ */
let maze    = {};
let pathRow = {};

function ensurePathRow(ci) {
  if (pathRow[ci] !== undefined) return pathRow[ci];
  if (ci === 0) { pathRow[0] = Math.floor(ROWS/2); return pathRow[0]; }
  const prev = ensurePathRow(ci - 1);
  const roll = Math.random();
  let next = prev + (roll < 0.22 ? -1 : roll < 0.44 ? 1 : 0);
  next = Math.max(1, Math.min(ROWS - 2, next));
  pathRow[ci] = next;
  return next;
}

function genColumn(ci) {
  if (maze[ci]) return maze[ci];
  const col = new Array(ROWS).fill(0);

  // Guaranteed spine: fill between previous path row and current
  const pr = ensurePathRow(ci);
  if (ci === 0) {
    col[pr] = 1;
  } else {
    const prevPR = ensurePathRow(ci - 1);
    const lo = Math.min(prevPR, pr), hi = Math.max(prevPR, pr);
    for (let r = lo; r <= hi; r++) col[r] = 1;
  }

  // Extra random open tiles (no guarantee of connectivity needed)
  for (let r = 1; r < ROWS - 1; r++) {
    if (!col[r] && Math.random() < 0.36) col[r] = 1;
  }

  maze[ci] = col;
  return col;
}

function ensureMaze(upTo) {
  for (let c = 0; c <= upTo; c++) if (!maze[c]) genColumn(c);
}

/* ═══════════════════════════════════════════════════════
   DRAW HELPERS
═══════════════════════════════════════════════════════ */
function drawHero(px, py, alpha=1, glow=1) {
  const cx = px + TILE/2, cy = py + TILE/2;
  ctx.save();
  ctx.globalAlpha = alpha;
  ctx.shadowColor = '#00ff00';
  ctx.shadowBlur  = 7 * glow;
  ctx.strokeStyle = `rgba(0,255,0,${0.75*glow})`;
  ctx.fillStyle   = '#090909';
  ctx.lineWidth   = 1.3;
  // Cloak
  ctx.beginPath();
  ctx.moveTo(cx-7, cy); ctx.lineTo(cx-11, cy+14);
  ctx.lineTo(cx+11, cy+14); ctx.lineTo(cx+7, cy);
  ctx.closePath(); ctx.fill(); ctx.stroke();
  // Hood
  ctx.beginPath();
  ctx.ellipse(cx, cy-7, 8, 10, 0, 0, Math.PI*2);
  ctx.fill(); ctx.stroke();
  // Face shadow
  ctx.fillStyle = '#040404'; ctx.strokeStyle = 'transparent';
  ctx.beginPath();
  ctx.ellipse(cx, cy-6, 4.5, 6.5, 0, 0, Math.PI*2);
  ctx.fill();
  // Eyes
  ctx.shadowBlur = 10 * glow;
  ctx.fillStyle  = '#00ff00';
  ctx.beginPath(); ctx.arc(cx-2.5, cy-8, 1.5, 0, Math.PI*2); ctx.fill();
  ctx.beginPath(); ctx.arc(cx+2.5, cy-8, 1.5, 0, Math.PI*2); ctx.fill();
  ctx.restore();
}

function drawSkull(px, py, scale=1, glow=1) {
  const cx = px + TILE/2*scale, cy = py + TILE/2*scale, s = scale;
  ctx.save();
  ctx.shadowColor = '#00ff00'; ctx.shadowBlur = 8*glow;
  ctx.strokeStyle = `rgba(0,255,0,${0.8*glow})`;
  ctx.fillStyle   = '#0c0c0c'; ctx.lineWidth = 1.3;
  // Cranium
  ctx.beginPath(); ctx.arc(cx, cy-2*s, 9*s, 0, Math.PI*2);
  ctx.fill(); ctx.stroke();
  // Jaw
  ctx.beginPath();
  ctx.moveTo(cx-7*s, cy+6*s); ctx.lineTo(cx-7*s, cy+12*s);
  ctx.lineTo(cx+7*s, cy+12*s); ctx.lineTo(cx+7*s, cy+6*s);
  ctx.closePath(); ctx.fill(); ctx.stroke();
  // Eye sockets
  ctx.fillStyle = `rgba(0,255,0,${0.9*glow})`; ctx.shadowBlur = 12*glow;
  ctx.beginPath(); ctx.ellipse(cx-3.5*s, cy-3*s, 2.8*s, 3.5*s, 0, 0, Math.PI*2); ctx.fill();
  ctx.beginPath(); ctx.ellipse(cx+3.5*s, cy-3*s, 2.8*s, 3.5*s, 0, 0, Math.PI*2); ctx.fill();
  // Nose
  ctx.fillStyle = `rgba(0,180,0,${0.7*glow})`; ctx.shadowBlur = 4*glow;
  ctx.beginPath();
  ctx.moveTo(cx-1.5*s, cy+2*s); ctx.lineTo(cx+1.5*s, cy+2*s);
  ctx.lineTo(cx, cy+5*s); ctx.closePath(); ctx.fill();
  // Teeth gaps
  ctx.fillStyle = '#080808'; ctx.shadowBlur = 0;
  for (let i = 0; i < 5; i++)
    ctx.fillRect(cx+(-2+i)*3*s - 0.5*s, cy+7*s, 2*s, 4*s);
  ctx.restore();
}

function drawTrophy(px, py, glow=1) {
  const cx = px + TILE/2, cy = py + TILE/2;
  ctx.save();
  ctx.shadowColor = '#ffd700';
  ctx.shadowBlur  = 14 * glow;
  ctx.strokeStyle = `rgba(255,215,0,${0.9*glow})`;
  ctx.fillStyle   = '#c8900a';
  ctx.lineWidth   = 1.5;
  // Cup bowl
  ctx.beginPath();
  ctx.moveTo(cx-8, cy-12);
  ctx.bezierCurveTo(cx-11, cy-4, cx-10, cy+2, cx-4, cy+5);
  ctx.lineTo(cx+4, cy+5);
  ctx.bezierCurveTo(cx+10, cy+2, cx+11, cy-4, cx+8, cy-12);
  ctx.closePath(); ctx.fill(); ctx.stroke();
  // Shine highlight
  ctx.fillStyle = 'rgba(255,255,160,0.28)';
  ctx.beginPath(); ctx.ellipse(cx-2, cy-7, 3, 5, -0.4, 0, Math.PI*2); ctx.fill();
  // Handles
  ctx.strokeStyle = `rgba(255,215,0,${0.8*glow})`; ctx.lineWidth = 1.5;
  ctx.beginPath(); ctx.arc(cx-9, cy-4, 3.5, Math.PI*0.4, Math.PI*1.6); ctx.stroke();
  ctx.beginPath(); ctx.arc(cx+9, cy-4, 3.5, -Math.PI*0.6, Math.PI*0.6); ctx.stroke();
  // Stem
  ctx.fillStyle   = '#c8900a';
  ctx.strokeStyle = `rgba(255,215,0,${0.9*glow})`;
  ctx.beginPath(); ctx.rect(cx-2, cy+5, 4, 7); ctx.fill(); ctx.stroke();
  // Base
  ctx.beginPath(); ctx.rect(cx-7, cy+12, 14, 3); ctx.fill(); ctx.stroke();
  // Gleam star on top
  const gl = 0.55 + 0.45*Math.sin(Date.now()*0.007);
  ctx.fillStyle  = `rgba(255,255,200,${gl*glow})`;
  ctx.shadowBlur = 10 * glow;
  ctx.beginPath(); ctx.arc(cx, cy-13, 2, 0, Math.PI*2); ctx.fill();
  ctx.restore();
}

/* ═══════════════════════════════════════════════════════
   GAME STATE
═══════════════════════════════════════════════════════ */
let phase       = 'lore';
let playerRow   = Math.floor(ROWS/2);
let playerWC    = 0;
let lives       = 1;
let score       = 0;
let invincible  = 0;
let hitFlash    = 0;
let killReason  = '';
let monsters    = [];
let parts       = [];
let spawnedUpTo = -1;
let surviveTime = 0;    // seconds of active play
let trophyWC    = -1;   // world-col of trophy; -1 = not spawned yet
let trophyRow   = -1;

// Intro state
let introY     = -40;
let introPhase = 0;
let introT     = 0;

// Kill / Win animation timers
let killT = 0;
let winT  = 0;

// Lore screen timer
let loreT = 0;

// Key repeat
const keysHeld    = {};
const keyLastMove = {};
const MOVE_MS     = 170;

/* ═══════════════════════════════════════════════════════
   RESET / START
═══════════════════════════════════════════════════════ */
function resetGame() {
  playerRow   = Math.floor(ROWS/2);
  playerWC    = 0;
  lives       = 1;
  score       = 0;
  invincible  = 0;
  hitFlash    = 0;
  monsters    = [];
  parts       = [];
  spawnedUpTo = -1;
  surviveTime = 0;
  trophyWC    = -1;
  trophyRow   = -1;
  maze        = {};
  pathRow     = {};
  ensureMaze(COLS + 8);
}

function startPlaying() {
  resetGame();
  phase = 'playing';
}

/* ═══════════════════════════════════════════════════════
   MAZE DRAWING
═══════════════════════════════════════════════════════ */
function drawMaze() {
  const startC = playerWC - PCOL;
  ctx.fillStyle = '#070707';
  ctx.fillRect(GX, GY, COLS*TILE, ROWS*TILE);

  for (let dc = 0; dc < COLS; dc++) {
    const wc  = startC + dc;
    const col = maze[wc] || new Array(ROWS).fill(0);
    const px  = GX + dc*TILE;
    for (let r = 0; r < ROWS; r++) {
      if (!col[r]) continue;
      const py = GY + r*TILE;
      ctx.fillStyle = '#111';
      ctx.fillRect(px+1, py+1, TILE-2, TILE-2);
      if (r%2 === 0) {
        ctx.fillStyle = 'rgba(0,255,0,0.012)';
        ctx.fillRect(px+1, py+1, TILE-2, TILE-2);
      }
    }
  }

  ctx.strokeStyle = 'rgba(0,255,0,0.18)'; ctx.lineWidth = 1;
  for (let dc = 0; dc < COLS; dc++) {
    const wc   = startC + dc;
    const col  = maze[wc]   || new Array(ROWS).fill(0);
    const prev = maze[wc-1] || new Array(ROWS).fill(0);
    const next = maze[wc+1] || new Array(ROWS).fill(0);
    const px   = GX + dc*TILE;
    for (let r = 0; r < ROWS; r++) {
      if (!col[r]) continue;
      const py = GY + r*TILE;
      if (!col[r-1]) { ctx.beginPath(); ctx.moveTo(px,py);      ctx.lineTo(px+TILE,py);      ctx.stroke(); }
      if (!col[r+1]) { ctx.beginPath(); ctx.moveTo(px,py+TILE); ctx.lineTo(px+TILE,py+TILE); ctx.stroke(); }
      if (!prev[r])  { ctx.beginPath(); ctx.moveTo(px,py);      ctx.lineTo(px,py+TILE);      ctx.stroke(); }
      if (!next[r])  { ctx.beginPath(); ctx.moveTo(px+TILE,py); ctx.lineTo(px+TILE,py+TILE); ctx.stroke(); }
    }
  }

  ctx.strokeStyle = 'rgba(0,255,0,0.22)'; ctx.lineWidth = 1;
  ctx.strokeRect(GX, GY, COLS*TILE, ROWS*TILE);
}

/* ═══════════════════════════════════════════════════════
   HUD
═══════════════════════════════════════════════════════ */
function drawHUD() {
  ctx.fillStyle = 'rgba(8,8,8,0.92)';
  ctx.fillRect(0, 0, W, GY);
  ctx.strokeStyle = 'rgba(0,255,0,0.18)'; ctx.lineWidth = 1;
  ctx.beginPath(); ctx.moveTo(0, GY); ctx.lineTo(W, GY); ctx.stroke();

  // Single life icon (left)
  ctx.fillStyle = '#555'; ctx.font = `9px ${MF}`;
  ctx.textAlign = 'left';
  ctx.fillText('LIFE', 12, 16);
  drawHero(12, 18, 1, 1);

  // Centre: countdown or trophy alert
  ctx.textAlign = 'center';
  if (trophyWC >= 0) {
    const blink = Math.floor(Date.now()/350) % 2;
    ctx.shadowColor = '#ffd700'; ctx.shadowBlur = blink ? 10 : 0;
    ctx.fillStyle   = blink ? '#ffd700' : 'rgba(255,215,0,0.45)';
    ctx.font        = `bold 11px ${MF}`;
    ctx.fillText('★  TROPHY AHEAD  ★', W/2, 22);
    ctx.shadowBlur  = 0;
    ctx.fillStyle   = '#555'; ctx.font = `9px ${MF}`;
    ctx.fillText('DEPTH  ' + playerWC, W/2, 38);
  } else {
    const rem = Math.max(0, WIN_TIME - surviveTime);
    const mm  = Math.floor(rem/60), ss = Math.floor(rem%60);
    const hot = rem < 60;
    ctx.fillStyle = hot ? '#ff6600' : '#555';
    ctx.font      = `9px ${MF}`;
    ctx.fillText('SURVIVE', W/2, 14);
    ctx.fillStyle = hot ? '#ff9900' : '#888';
    ctx.font      = `bold 14px ${MF}`;
    ctx.fillText(mm + ':' + (ss < 10 ? '0' : '') + ss, W/2, 30);
    ctx.fillStyle = '#555'; ctx.font = `9px ${MF}`;
    ctx.fillText('DEPTH  ' + playerWC, W/2, 44);
  }

  // Score (right)
  ctx.fillStyle = '#00ff00'; ctx.font = `bold 17px ${MF}`;
  ctx.textAlign = 'right';
  ctx.fillText(String(score).padStart(7,'0'), W-12, 28);
  ctx.fillStyle = '#444'; ctx.font = `9px ${MF}`;
  ctx.fillText('SCORE', W-12, 40);

  // Danger ping
  const near = monsters.some(m => Math.abs(m.wc-playerWC)<=4 && Math.abs(m.row-playerRow)<=2);
  if (near) {
    const p = 0.5 + 0.5*Math.sin(Date.now()*0.013);
    ctx.fillStyle = `rgba(255,30,30,${p})`;
    ctx.font      = `9px ${MF}`; ctx.textAlign = 'left';
    ctx.fillText('! DANGER !', 58, 32);
  }
}

/* ═══════════════════════════════════════════════════════
   MONSTERS  (horizontal / vertical / diagonal)
═══════════════════════════════════════════════════════ */
function spawnMonsters() {
  const front = playerWC + COLS - 1;
  if (front <= spawnedUpTo) return;
  for (let c = spawnedUpTo+1; c <= front; c++) {
    const col = maze[c] || [];
    for (let r = 0; r < ROWS; r++) {
      if (col[r] && Math.abs(c - playerWC) > 4 && Math.random() < 0.08) {
        // style 0 = horiz, 1 = vert, 2 = diagonal
        const style = Math.floor(Math.random()*3);
        monsters.push({
          wc:    c, row: r,
          dirWC: style === 1 ? 0 : (Math.random()<0.5 ? 1 : -1),
          dirRow:style === 0 ? 0 : (Math.random()<0.5 ? 1 : -1),
          style, timer: Math.random()*550
        });
      }
    }
  }
  spawnedUpTo = front;
}

function canWalk(wc, row) {
  return row >= 1 && row < ROWS-1 && (maze[wc]||[])[row] === 1;
}

function updateMonsters(dt) {
  const MS = 520;
  for (let i = monsters.length-1; i >= 0; i--) {
    const m = monsters[i];
    m.timer += dt*1000;
    if (m.timer < MS) continue;
    m.timer = 0;

    const nwc = m.wc + m.dirWC, nrow = m.row + m.dirRow;

    if (canWalk(nwc, nrow)) {
      m.wc = nwc; m.row = nrow;
    } else if (m.style === 2) {
      const hOk = canWalk(nwc, m.row);
      const vOk = canWalk(m.wc, m.row + m.dirRow);
      if      (hOk) { m.wc  += m.dirWC; }
      else if (vOk) { m.row += m.dirRow; }
      else {
        m.dirWC *= -1; m.dirRow *= -1;
        // If reversed diagonal is also stuck, remove
        if (!canWalk(m.wc+m.dirWC, m.row) && !canWalk(m.wc, m.row+m.dirRow))
          { monsters.splice(i,1); continue; }
      }
    } else if (m.style === 0) {
      m.dirWC *= -1;
      // If reversed direction also blocked (isolated tile), remove
      if (!canWalk(m.wc + m.dirWC, m.row))
        { monsters.splice(i,1); continue; }
    } else {
      m.dirRow *= -1;
      if (!canWalk(m.wc, m.row + m.dirRow))
        { monsters.splice(i,1); continue; }
    }
  }
  // Cull far-left monsters
  monsters = monsters.filter(m => m.wc >= playerWC - PCOL - 2);
}

/* ═══════════════════════════════════════════════════════
   COLLISION / DAMAGE
═══════════════════════════════════════════════════════ */
function checkCollision() {
  if (invincible > 0) return;
  for (const m of monsters) {
    if (m.wc === playerWC && m.row === playerRow) { takeDamage(); return; }
  }
}

function takeDamage() {
  lives--;
  hitFlash = 600;
  // 1 life only — die immediately
  if (lives <= 0) { killReason = 'dead'; triggerKill(); }
  else            { invincible = 2200; }
}

function checkTrophy() {
  if (trophyWC < 0) return;
  if (playerWC === trophyWC && playerRow === trophyRow) triggerWin();
}

function triggerKill() {
  phase = 'kill'; killT = 0;
  const px = GX + PCOL*TILE + TILE/2;
  const py = GY + playerRow*TILE + TILE/2;
  for (let i = 0; i < 35; i++) {
    const ang = Math.random()*Math.PI*2, sp = 1.5+Math.random()*6;
    parts.push({
      x:px, y:py,
      vx:Math.cos(ang)*sp, vy:Math.sin(ang)*sp - 1,
      life:1, dc:0.012+Math.random()*0.022,
      color: Math.random()<0.5 ? '#00ff00' : '#ff2200',
    });
  }
}

function triggerWin() {
  phase = 'win'; winT = 0;
}

/* ═══════════════════════════════════════════════════════
   MOVEMENT  (all 4 directions; left no longer kills)
═══════════════════════════════════════════════════════ */
function moveRight() {
  const nwc = playerWC + 1;
  ensureMaze(nwc + COLS + 5);
  if ((maze[nwc]||[])[playerRow] === 1) {
    playerWC++; score += 10;
    spawnMonsters(); checkTrophy(); checkCollision();
  }
}
function moveUp() {
  const nr = playerRow - 1;
  if (nr >= 1 && (maze[playerWC]||[])[nr] === 1) {
    playerRow = nr; checkTrophy(); checkCollision();
  }
}
function moveDown() {
  const nr = playerRow + 1;
  if (nr < ROWS-1 && (maze[playerWC]||[])[nr] === 1) {
    playerRow = nr; checkTrophy(); checkCollision();
  }
}
function moveLeft() {
  if (playerWC <= 0) return;
  const nwc = playerWC - 1;
  if ((maze[nwc]||[])[playerRow] === 1) {
    playerWC--; checkCollision();
  }
}

function handleKey(code) {
  if (phase !== 'playing') return;
  if      (code === 'ArrowRight') moveRight();
  else if (code === 'ArrowUp')    moveUp();
  else if (code === 'ArrowDown')  moveDown();
  else if (code === 'ArrowLeft')  moveLeft();
}

/* ═══════════════════════════════════════════════════════
   UPDATE
═══════════════════════════════════════════════════════ */
function updatePlaying(dt) {
  // Key repeat
  for (const [code, held] of Object.entries(keysHeld)) {
    if (!held) continue;
    const last = keyLastMove[code] || 0, now = performance.now();
    if (now - last >= MOVE_MS) { keyLastMove[code] = now; handleKey(code); }
  }

  if (invincible > 0) invincible -= dt*1000;
  if (hitFlash   > 0) hitFlash   -= dt*1000;

  // Survival clock
  surviveTime += dt;

  // Spawn trophy after WIN_TIME seconds
  if (trophyWC < 0 && surviveTime >= WIN_TIME) {
    trophyWC = playerWC + COLS - 1;
    ensureMaze(trophyWC + 2);
    // Place on guaranteed path row; force tile open
    trophyRow = pathRow[trophyWC] !== undefined ? pathRow[trophyWC] : Math.floor(ROWS/2);
    if (maze[trophyWC]) maze[trophyWC][trophyRow] = 1;
  }

  updateMonsters(dt);
  ensureMaze(playerWC + COLS + 5);
}

function updateKill(dt) {
  killT += dt*1000;
  for (let i = parts.length-1; i >= 0; i--) {
    const p = parts[i];
    p.x += p.vx; p.y += p.vy; p.vy += 0.18;
    p.vx *= 0.94; p.life -= p.dc;
    if (p.life <= 0) parts.splice(i,1);
  }
  if (killT >= 3000) phase = 'over';
}

function updateWin(dt) {
  winT += dt*1000;
  // stays on win phase; player presses space to restart
}

function updateIntro(dt) {
  introT += dt*1000;
  if (introPhase === 0) {
    introY = -40 + Math.pow(introT/1600, 1.6) * (H + 80);
    if (introT >= 1600) { introPhase = 1; introT = 0; }
  } else if (introPhase === 1) {
    if (introT >= 380) { introPhase = 2; introT = 0; }
  } else if (introPhase === 2) {
    if (introT >= 900) phase = 'start';
  }
}

/* ═══════════════════════════════════════════════════════
   DRAW PHASES
═══════════════════════════════════════════════════════ */
function drawPlaying(ts) {
  ctx.fillStyle = '#07070a'; ctx.fillRect(0,0,W,H);
  drawMaze();

  // Trophy
  if (trophyWC >= 0) {
    const startC = playerWC - PCOL;
    const dc = trophyWC - startC;
    if (dc >= 0 && dc < COLS) {
      const tg = 1 + 0.55*Math.sin(ts*0.004);
      drawTrophy(GX + dc*TILE, GY + trophyRow*TILE, tg);
    }
  }

  // Monsters
  const startC = playerWC - PCOL;
  for (const m of monsters) {
    const dc = m.wc - startC;
    if (dc < 0 || dc >= COLS) continue;
    const dist = Math.abs(m.wc-playerWC) + Math.abs(m.row-playerRow);
    drawSkull(GX + dc*TILE, GY + m.row*TILE, 1, Math.max(0.3, 1-dist/10));
  }

  // Player (blink during invincibility)
  const blink = invincible > 0 && Math.floor(ts/130)%2 === 0;
  if (!blink) drawHero(GX + PCOL*TILE, GY + playerRow*TILE);

  // Hit flash
  if (hitFlash > 0) {
    ctx.fillStyle = `rgba(255,0,0,${(hitFlash/600)*0.45})`;
    ctx.fillRect(GX, GY, COLS*TILE, ROWS*TILE);
  }

  drawHUD();
}

function drawIntro(ts) {
  ctx.fillStyle = '#030305'; ctx.fillRect(0,0,W,H);
  ctx.strokeStyle = 'rgba(0,255,0,0.12)'; ctx.lineWidth = 1;
  for (let i = 0; i < 18; i++) {
    const x = 20 + i*30;
    const len = 25 + Math.sin(ts*0.001+i*0.8)*12;
    const yBase = ((introY+40+i*43)%H+H)%H;
    ctx.beginPath(); ctx.moveTo(x, yBase-len); ctx.lineTo(x, yBase+len); ctx.stroke();
  }
  ctx.fillStyle = 'rgba(0,255,0,0.06)';
  for (let i = 0; i < 40; i++) {
    const sx = ((i*137+73)%W), sy = ((introY*0.3+i*61)%H+H)%H;
    ctx.beginPath(); ctx.arc(sx,sy,0.8,0,Math.PI*2); ctx.fill();
  }
  if (introPhase === 0 && introY > -40 && introY < H+40) {
    for (let i = 4; i >= 1; i--) drawHero(W/2-TILE/2, introY-i*22, i*0.08, 0.3);
    drawHero(W/2-TILE/2, introY, 1, 1.5);
  }
  if (introPhase === 1) {
    const al = 1-(introT/380);
    ctx.fillStyle = `rgba(0,255,0,${al*0.5})`; ctx.fillRect(0,0,W,H);
    ctx.fillStyle = `rgba(255,255,255,${al*0.3})`; ctx.fillRect(0,0,W,H);
  }
  if (introPhase === 2) {
    const al = Math.min(1, introT/600);
    ctx.fillStyle = `rgba(0,255,0,${al*0.85})`;
    ctx.font = `bold 11px ${MF}`; ctx.textAlign = 'center';
    ctx.fillText('> ENTERING THE ABYSS...', W/2, H/2+20);
  }
}

function drawStart(ts) {
  ctx.fillStyle = '#07070a'; ctx.fillRect(0,0,W,H);
  drawMaze();
  ctx.fillStyle = 'rgba(5,5,5,0.80)'; ctx.fillRect(0,0,W,H);
  ctx.textAlign = 'center';

  // ── Title ──
  ctx.fillStyle = 'rgba(0,255,0,0.6)'; ctx.font = `11px ${MF}`;
  ctx.fillText('> SYSTEM ONLINE  |  DUNGEON LOADED', W/2, H/2-100);
  ctx.shadowColor = '#00ff00'; ctx.shadowBlur = 18;
  ctx.fillStyle = '#00ff00'; ctx.font = `bold 30px ${MF}`;
  ctx.fillText('INFINITE  MAZE', W/2, H/2-66);
  ctx.shadowBlur = 0;
  ctx.fillStyle = '#555'; ctx.font = `12px ${MF}`;
  ctx.fillText('INFINITE MAZE  —  NO WAY BACK', W/2, H/2-42);

  // ── Hero ──
  const g = 1 + 0.6*Math.sin(ts*0.003);
  drawHero(W/2-TILE/2, H/2-26, 1, g);

  // ── Difficulty selector ──
  const diffs = [
    { id:1, label:'① EASY',   time:'3 MIN', col:'#00cc44' },
    { id:2, label:'② MEDIUM', time:'5 MIN', col:'#ffaa00' },
    { id:3, label:'③ HARD',   time:'10 MIN', col:'#ff3333' },
  ];
  ctx.font = `10px ${MF}`;
  ctx.fillStyle = '#444';
  ctx.fillText('SELECT DIFFICULTY  ( press  1 / 2 / 3 )', W/2, H/2+22);

  const boxW=84, boxH=28, gap=10;
  const totalW = diffs.length*(boxW+gap)-gap;
  let bx = W/2 - totalW/2;
  for (const d of diffs) {
    const sel = difficulty === d.id;
    const x = bx, y = H/2+30, w = boxW, h = boxH;
    // box
    ctx.strokeStyle = sel ? d.col : '#333';
    ctx.lineWidth   = sel ? 1.5 : 0.8;
    ctx.shadowColor = sel ? d.col : 'transparent';
    ctx.shadowBlur  = sel ? 8 : 0;
    ctx.strokeRect(x, y, w, h);
    ctx.shadowBlur = 0;
    // fill
    ctx.fillStyle = sel ? `${d.col}22` : 'transparent';
    ctx.fillRect(x, y, w, h);
    // text
    ctx.textAlign = 'center';
    ctx.fillStyle = sel ? d.col : '#555';
    ctx.font = `bold ${sel?10:9}px ${MF}`;
    ctx.fillText(d.label, x+w/2, y+11);
    ctx.font = `${sel?9:8}px ${MF}`;
    ctx.fillStyle = sel ? '#ffffff99' : '#444';
    ctx.fillText(`TROPHY @ ${d.time}`, x+w/2, y+22);
    bx += boxW+gap;
  }
  ctx.lineWidth = 1;

  // ── Info ──
  ctx.textAlign = 'center';
  ctx.fillStyle = '#444'; ctx.font = `10px ${MF}`;
  ctx.fillText('↑ ↓ ← → MOVE  ·  ONE LIFE  ·  SKULL = INSTANT DEATH', W/2, H/2+76);
  ctx.fillStyle = 'rgba(0,255,0,0.28)'; ctx.font = `9px ${MF}`;
  ctx.fillText('STANDING STILL → MONSTERS PASS THROUGH YOU', W/2, H/2+90);

  // ── Blink prompt ──
  const blink = Math.floor(ts/600)%2;
  ctx.fillStyle = blink ? '#00ff00' : '#1a3a1a'; ctx.font = `13px ${MF}`;
  ctx.fillText('[ PRESS  SPACE  TO  DESCEND ]', W/2, H/2+112);
}

function drawKill(ts) {
  ctx.fillStyle = 'rgba(3,3,3,0.94)'; ctx.fillRect(0,0,W,H);
  for (const p of parts) {
    ctx.save(); ctx.globalAlpha = Math.max(0, p.life);
    ctx.fillStyle = p.color; ctx.shadowColor = p.color; ctx.shadowBlur = 5;
    ctx.fillRect(p.x-2, p.y-2, 4, 4); ctx.restore();
  }
  if (killT < 700) {
    const pulse = Math.sin(killT*0.025)*0.28;
    if (pulse > 0) { ctx.fillStyle = `rgba(255,0,0,${pulse})`; ctx.fillRect(0,0,W,H); }
  }
  if (killT > 600) {
    const al = Math.min(1,(killT-600)/500);
    const sc = 1.5 + Math.min(1.5,(killT-600)/600);
    ctx.save(); ctx.globalAlpha = al;
    drawSkull(W/2 - TILE/2*sc, H/2 - TILE/2*sc - 20, sc, 1.8);
    ctx.restore();
  }
  if (killT > 1300) {
    const al = Math.min(1,(killT-1300)/500);
    ctx.textAlign = 'center';
    ctx.shadowColor = '#00ff00'; ctx.shadowBlur = 10;
    ctx.fillStyle   = `rgba(0,255,0,${al})`;
    ctx.font        = `bold 17px ${MF}`;
    ctx.fillText('> PROCESS  TERMINATED', W/2, H/2+90);
    ctx.shadowBlur  = 0;
  }
}

function drawOver(ts) {
  ctx.fillStyle = 'rgba(3,3,3,0.96)'; ctx.fillRect(0,0,W,H);
  ctx.strokeStyle = 'rgba(0,255,0,0.14)'; ctx.lineWidth = 1; ctx.setLineDash([7,14]);
  ctx.beginPath(); ctx.arc(W/2,H/2,180,0,Math.PI*2); ctx.stroke();
  ctx.setLineDash([]);
  ctx.textAlign = 'center';
  ctx.fillStyle = 'rgba(0,255,0,0.7)'; ctx.font = `11px ${MF}`;
  ctx.fillText('> SYSTEM FAILURE', W/2, H/2-80);
  ctx.shadowColor = '#00ff00'; ctx.shadowBlur = 14;
  ctx.fillStyle = '#00ff00'; ctx.font = `bold 34px ${MF}`;
  ctx.fillText('TERMINATED', W/2, H/2-48);
  ctx.shadowBlur = 0;
  ctx.fillStyle = '#555'; ctx.font = `12px ${MF}`;
  ctx.fillText('> CONSUMED BY THE MAZE', W/2, H/2-22);
  ctx.fillStyle = '#ddd'; ctx.font = `bold 26px ${MF}`;
  ctx.fillText(String(score).padStart(7,'0'), W/2, H/2+18);
  ctx.fillStyle = '#444'; ctx.font = `10px ${MF}`;
  ctx.fillText('FINAL SCORE  |  DEPTH ' + playerWC, W/2, H/2+36);
  const blink = Math.floor(ts/700)%2;
  ctx.fillStyle = blink ? '#00ff00' : '#1a3a1a'; ctx.font = `13px ${MF}`;
  ctx.fillText('[ SPACE / ENTER  TO  RESTART ]', W/2, H/2+80);
}

function drawWin(ts) {
  /* Timeline (winT in ms):
     0–1800   : maze ghost + hero approaches trophy, trophy glow intensifies
     600–2000 : "$ sudo su" fades in (gold)
     1800–3200: blinding white-gold flash (bell curve peak ~2300ms)
     2800+    : dark settles, big trophy, "结局：终结噩梦" in gold
  */
  ctx.fillStyle = 'rgba(3,3,5,0.97)'; ctx.fillRect(0,0,W,H);

  // ── Phase A: maze + trophy + hero ──
  if (winT < 1800) {
    ctx.save(); ctx.globalAlpha = 0.15; drawMaze(); ctx.restore();
    const tg = 1 + Math.min(3.5, winT/350);
    drawTrophy(GX + PCOL*TILE, GY + playerRow*TILE, tg);
    // Hero one step behind, leaning in
    drawHero(GX + (PCOL-1)*TILE, GY + playerRow*TILE, 1, 1.2);
  }

  // ── Phase B: sudo su (gold) ──
  if (winT > 600 && winT < 2600) {
    const al = Math.min(1, (winT-600)/700);
    ctx.save();
    ctx.globalAlpha   = al;
    ctx.shadowColor   = '#ffd700'; ctx.shadowBlur = 24;
    ctx.fillStyle     = '#ffd700';
    ctx.font          = `bold 26px ${MF}`;
    ctx.textAlign     = 'center';
    ctx.fillText('$ sudo su', W/2, H*0.44);
    ctx.shadowBlur    = 8;
    ctx.fillStyle     = 'rgba(255,215,0,0.55)';
    ctx.font          = `12px ${MF}`;
    ctx.fillText('> ROOT ACCESS GRANTED', W/2, H*0.44+28);
    ctx.restore();
  }

  // ── Phase C: blinding white-gold flash ──
  if (winT > 1800 && winT < 3400) {
    const t  = (winT - 1800) / 1600;
    const al = t < 0.4 ? t/0.4 : 1-(t-0.4)/0.6;
    if (t < 0.55) {
      ctx.fillStyle = `rgba(255,215,0,${(1-t/0.55)*0.5})`; ctx.fillRect(0,0,W,H);
    }
    ctx.fillStyle = `rgba(255,255,255,${al})`; ctx.fillRect(0,0,W,H);
  }

  // ── Phase D: ending title ──
  if (winT > 2900) {
    const al = Math.min(1, (winT-2900)/900);

    // Dark background
    ctx.fillStyle = `rgba(3,2,0,${al*0.92})`; ctx.fillRect(0,0,W,H);

    // Large centred trophy
    if (al > 0.25) {
      ctx.save(); ctx.globalAlpha = (al-0.25)/0.75;
      const sc = 2.6;
      drawTrophy(W/2 - TILE/2*sc, H/2 - TILE/2*sc - 44, sc, 2.2);
      ctx.restore();
    }

    ctx.save();
    ctx.globalAlpha = al;
    ctx.textAlign   = 'center';

    // Ending label
    ctx.shadowColor = '#ffd700'; ctx.shadowBlur = 18;
    ctx.fillStyle   = 'rgba(255,215,0,0.75)';
    ctx.font        = `13px ${MF}`;
    ctx.fillText('> ENDING', W/2, H*0.62);

    // Main title
    ctx.shadowBlur  = 36;
    ctx.fillStyle   = '#fff8c0';
    ctx.font        = `bold 28px ${MF}`;
    ctx.fillText('NIGHTMARE  TERMINATED', W/2, H*0.62+42);

    // Sub-line
    ctx.shadowBlur  = 10;
    ctx.fillStyle   = 'rgba(255,215,0,0.5)';
    ctx.font        = `11px ${MF}`;
    ctx.fillText('THE DARKNESS ENDS HERE', W/2, H*0.62+68);

    // Blink restart hint (appears late)
    if (winT > 5000) {
      const bl = Math.floor(ts/700)%2;
      ctx.shadowBlur = 0;
      ctx.fillStyle  = bl ? 'rgba(255,215,0,0.8)' : 'rgba(255,215,0,0.2)';
      ctx.font       = `11px ${MF}`;
      ctx.fillText('[ SPACE / ENTER  TO  RESTART ]', W/2, H*0.62+96);
    }
    ctx.restore();
  }
}

/* ═══════════════════════════════════════════════════════
   LORE SCREEN
═══════════════════════════════════════════════════════ */
function updateLore(dt) {
  loreT += dt * 1000;
}

function drawLore(ts) {
  ctx.fillStyle = '#020204'; ctx.fillRect(0,0,W,H);

  // Subtle scan-line texture
  for (let y = 0; y < H; y += 3) {
    ctx.fillStyle = 'rgba(0,40,0,0.05)';
    ctx.fillRect(0, y, W, 1);
  }

  ctx.textAlign = 'center';

  // Each line: { t=delay ms, y, txt, col, sz, bold }
  const L = [
    { t:   0, y: 40,  txt: '> ESTABLISHING SECURE CONNECTION...',        col:'rgba(0,255,0,0.65)', sz:10, bold:false },
    { t: 180, y: 55,  txt: '> LOCATION: [CLASSIFIED]  ·  USER: GHOST',   col:'rgba(0,255,0,0.38)', sz:10, bold:false },
    { t: 350, y: 73,  txt: '────────────────────────────────────────',    col:'rgba(0,255,0,0.12)', sz:10, bold:false },
    { t: 620, y:106,  txt: 'You are a hacker.',                           col:'#cccccc',            sz:13, bold:false },
    { t: 950, y:127,  txt: 'You chose to change the world.',              col:'#cccccc',            sz:13, bold:false },
    { t:1450, y:160,  txt: 'While browsing the web, you slipped —',       col:'#999999',            sz:11, bold:false },
    { t:1750, y:176,  txt: 'deep into something that should not exist.',  col:'#999999',            sz:11, bold:false },
    { t:2350, y:210,  txt: 'T H E   R E A L   D A R K   N E T',          col:'#00ff00',            sz:14, bold:true  },
    { t:2950, y:246,  txt: 'Buried within its encrypted labyrinth',       col:'#666666',            sz:10, bold:false },
    { t:3150, y:261,  txt: 'lurks a parasite — a shadow organization',    col:'#666666',            sz:10, bold:false },
    { t:3350, y:276,  txt: 'that has corrupted the core systems of the world.', col:'#666666',      sz:10, bold:false },
    { t:3850, y:308,  txt: 'But you found the weakness.',                 col:'#bbbbbb',            sz:11, bold:false },
    { t:4150, y:324,  txt: 'Layer by layer.  Exploit by exploit.',        col:'#bbbbbb',            sz:11, bold:false },
    { t:4650, y:354,  txt: 'Navigate deep enough to seize ROOT ACCESS.',  col:'#aaaaaa',            sz:11, bold:false },
    { t:5100, y:376,  txt: 'Terminate everything.',                       col:'#dddddd',            sz:13, bold:true  },
  ];

  for (const l of L) {
    const elapsed = loreT - l.t;
    if (elapsed < 0) continue;
    const alpha = Math.min(1, elapsed / 350);
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.fillStyle   = l.col;
    ctx.font        = `${l.bold ? 'bold ' : ''}${l.sz}px ${MF}`;
    if (l.bold && l.col === '#00ff00') { ctx.shadowColor = '#00ff00'; ctx.shadowBlur = 14; }
    ctx.fillText(l.txt, W/2, l.y);
    ctx.restore();
  }

  // Blinking prompt — appears after all text has faded in
  if (loreT > 5800) {
    const blink = Math.floor(ts/650) % 2;
    ctx.fillStyle = blink ? '#00ff00' : '#1a3a1a';
    ctx.font      = `bold 13px ${MF}`;
    ctx.fillText('[ PRESS  SPACE  TO  JACK  IN ]', W/2, 428);
  }
}

/* ═══════════════════════════════════════════════════════
   AUDIO ENGINE  (Web Audio API · no external files)
═══════════════════════════════════════════════════════ */
let _ac       = null;
let _mGain    = null;
let _curStop  = null;
let _curMCat  = '';
let _rhythmId = null;

function _getAC() {
  if (!_ac) {
    _ac = new (window.AudioContext || window.webkitAudioContext)();
    _mGain = _ac.createGain();
    _mGain.gain.value = 0.20;
    _mGain.connect(_ac.destination);
  }
  if (_ac.state === 'suspended') _ac.resume();
  return _ac;
}

function _killOld(fadeS) {
  if (_rhythmId) { clearInterval(_rhythmId); _rhythmId = null; }
  if (_curStop)  { _curStop(fadeS); _curStop = null; }
}

// ── Ambient drone (lore / intro / start) ──────────────────
function _playAmbient() {
  const ac = _getAC(), now = ac.currentTime;
  const fg = ac.createGain();
  fg.gain.setValueAtTime(0, now);
  fg.gain.linearRampToValueAtTime(1, now + 3);
  fg.connect(_mGain);

  const o1 = ac.createOscillator(); o1.type='sine';     o1.frequency.value=36;
  const g1 = ac.createGain();       g1.gain.value=0.55; o1.connect(g1); g1.connect(fg);

  const o2 = ac.createOscillator(); o2.type='sine';     o2.frequency.value=72;
  const g2 = ac.createGain();       g2.gain.value=0.18; o2.connect(g2); g2.connect(fg);

  const o3 = ac.createOscillator(); o3.type='triangle'; o3.frequency.value=108;
  const g3 = ac.createGain();       g3.gain.value=0.06; o3.connect(g3); g3.connect(fg);

  const lfo1 = ac.createOscillator(); lfo1.type='sine'; lfo1.frequency.value=0.07;
  const lG1  = ac.createGain();       lG1.gain.value=0.9;
  lfo1.connect(lG1); lG1.connect(o1.frequency); lG1.connect(o2.frequency);

  const o4   = ac.createOscillator(); o4.type='triangle'; o4.frequency.value=220;
  const lfo2 = ac.createOscillator(); lfo2.type='sine';   lfo2.frequency.value=0.18;
  const g4   = ac.createGain(); g4.gain.value=0.02;
  const lG2  = ac.createGain(); lG2.gain.value=0.016;
  lfo2.connect(lG2); lG2.connect(g4.gain);
  o4.connect(g4); g4.connect(fg);

  [o1,o2,o3,o4,lfo1,lfo2].forEach(o => o.start());

  _curStop = fadeS => {
    fg.gain.setTargetAtTime(0, ac.currentTime, (fadeS||1.2)/3);
    const t = ac.currentTime + (fadeS||1.2) + 0.5;
    [o1,o2,o3,o4,lfo1,lfo2].forEach(o => { try{o.stop(t);}catch(e){} });
  };
}

// ── Tension music (playing) ────────────────────────────────
function _playTension() {
  const ac = _getAC(), now = ac.currentTime;
  const fg = ac.createGain();
  fg.gain.setValueAtTime(0, now);
  fg.gain.linearRampToValueAtTime(1, now + 2);
  fg.connect(_mGain);

  const sub  = ac.createOscillator(); sub.type='sine';     sub.frequency.value=40;
  const subF = ac.createBiquadFilter(); subF.type='lowpass'; subF.frequency.value=100;
  const subG = ac.createGain(); subG.gain.value=0.40;
  sub.connect(subF); subF.connect(subG); subG.connect(fg);

  const saw  = ac.createOscillator(); saw.type='sawtooth'; saw.frequency.value=55;
  const sawF = ac.createBiquadFilter(); sawF.type='lowpass'; sawF.frequency.value=140;
  const sawG = ac.createGain(); sawG.gain.value=0.14;
  saw.connect(sawF); sawF.connect(sawG); sawG.connect(fg);

  const lfo  = ac.createOscillator(); lfo.type='sine'; lfo.frequency.value=0.04;
  const lG   = ac.createGain(); lG.gain.value=50;
  lfo.connect(lG); lG.connect(sawF.frequency);

  const hi   = ac.createOscillator(); hi.type='square'; hi.frequency.value=220;
  const hiF  = ac.createBiquadFilter(); hiF.type='bandpass'; hiF.frequency.value=300; hiF.Q.value=5;
  const hiG  = ac.createGain(); hiG.gain.value=0.035;
  hi.connect(hiF); hiF.connect(hiG); hiG.connect(fg);

  [sub, saw, lfo, hi].forEach(o => o.start());

  const BPM=110, beatMs=60000/BPM;
  let beat=0;
  _rhythmId = setInterval(() => {
    if (!_ac || _ac.state!=='running') return;
    const t = ac.currentTime;
    if (beat%4===0 || beat%4===2) {
      const k=ac.createOscillator(); k.type='sine';
      k.frequency.setValueAtTime(90,t); k.frequency.exponentialRampToValueAtTime(0.01,t+0.13);
      const kg=ac.createGain(); kg.gain.setValueAtTime(0.55,t); kg.gain.exponentialRampToValueAtTime(0.001,t+0.15);
      k.connect(kg); kg.connect(fg); k.start(t); k.stop(t+0.18);
    }
    if (beat%4===1 || beat%4===3) {
      const sb=ac.createBuffer(1,Math.floor(ac.sampleRate*0.08),ac.sampleRate);
      const sd=sb.getChannelData(0); for(let i=0;i<sd.length;i++) sd[i]=(Math.random()*2-1)*(1-i/sd.length);
      const sn=ac.createBufferSource(); sn.buffer=sb;
      const sf=ac.createBiquadFilter(); sf.type='bandpass'; sf.frequency.value=2500;
      const sg=ac.createGain(); sg.gain.value=0.16;
      sn.connect(sf); sf.connect(sg); sg.connect(fg); sn.start(t);
    }
    const hb=ac.createBuffer(1,Math.floor(ac.sampleRate*0.04),ac.sampleRate);
    const hd=hb.getChannelData(0); for(let i=0;i<hd.length;i++) hd[i]=(Math.random()*2-1)*(1-i/hd.length);
    const hh=ac.createBufferSource(); hh.buffer=hb;
    const hf=ac.createBiquadFilter(); hf.type='highpass'; hf.frequency.value=9000;
    const hg=ac.createGain(); hg.gain.value=0.065;
    hh.connect(hf); hf.connect(hg); hg.connect(fg); hh.start(t);
    beat++;
  }, beatMs);

  _curStop = fadeS => {
    if (_rhythmId) { clearInterval(_rhythmId); _rhythmId = null; }
    fg.gain.setTargetAtTime(0, ac.currentTime, (fadeS||1.2)/3);
    const t = ac.currentTime + (fadeS||1.2) + 0.5;
    [sub,saw,lfo,hi].forEach(o => { try{o.stop(t);}catch(e){} });
  };
}

// ── Kill sting (one-shot) ──────────────────────────────────
function _playKillSting() {
  const ac = _getAC(), now = ac.currentTime;
  const fg = ac.createGain(); fg.gain.value=1; fg.connect(_mGain);

  const o=ac.createOscillator(); o.type='sawtooth';
  o.frequency.setValueAtTime(180,now); o.frequency.exponentialRampToValueAtTime(18,now+1.8);
  const g=ac.createGain();
  g.gain.setValueAtTime(0.55,now); g.gain.exponentialRampToValueAtTime(0.001,now+2.2);
  o.connect(g); g.connect(fg); o.start(now); o.stop(now+2.5);

  const len=Math.floor(ac.sampleRate*0.35);
  const buf=ac.createBuffer(1,len,ac.sampleRate);
  const d=buf.getChannelData(0); for(let i=0;i<len;i++) d[i]=(Math.random()*2-1)*(1-i/len*0.7);
  const ns=ac.createBufferSource(); ns.buffer=buf;
  const nf=ac.createBiquadFilter(); nf.type='lowpass'; nf.frequency.value=600;
  const ng=ac.createGain(); ng.gain.value=0.32;
  ns.connect(nf); nf.connect(ng); ng.connect(fg); ns.start(now);

  _curStop = () => {};
}

// ── Win arpeggio + gold sustain ────────────────────────────
function _playWin() {
  const ac = _getAC(), now = ac.currentTime;
  const fg = ac.createGain(); fg.gain.value=1; fg.connect(_mGain);

  const notes=[220,277.18,329.63,440,554.37,659.25,880,1108.73];
  notes.forEach((freq,i) => {
    const t=now+i*0.22;
    const o=ac.createOscillator(); o.type='triangle'; o.frequency.value=freq;
    const g=ac.createGain();
    g.gain.setValueAtTime(0,t); g.gain.linearRampToValueAtTime(0.14,t+0.04);
    g.gain.exponentialRampToValueAtTime(0.001,t+1.5);
    o.connect(g); g.connect(fg); o.start(t); o.stop(t+1.6);
  });

  const droneT=now+notes.length*0.22+0.3;
  const d1=ac.createOscillator(); d1.type='sine';     d1.frequency.value=110;
  const d2=ac.createOscillator(); d2.type='sine';     d2.frequency.value=220;
  const d3=ac.createOscillator(); d3.type='triangle'; d3.frequency.value=440;
  const dg=ac.createGain(); dg.gain.setValueAtTime(0,droneT); dg.gain.linearRampToValueAtTime(0.16,droneT+2);
  [d1,d2,d3].forEach(o => { o.connect(dg); o.start(droneT); });
  dg.connect(fg);

  _curStop = fadeS => {
    fg.gain.setTargetAtTime(0, ac.currentTime, (fadeS||1.2)/3);
    const t=ac.currentTime+(fadeS||1.2)+0.5;
    [d1,d2,d3].forEach(o => { try{o.stop(t);}catch(e){} });
  };
}

// ── Phase → category mapping ───────────────────────────────
const _MCAT = { lore:'ambient', intro:'ambient', start:'ambient',
                playing:'tension', kill:'kill', over:'silence', win:'win' };

function _updateMusic() {
  if (!_ac) return;
  const cat = _MCAT[phase] || 'silence';
  if (cat === _curMCat) return;
  const prev = _curMCat;
  _curMCat = cat;
  if (prev && prev !== 'kill') _killOld(1.2);
  if      (cat === 'ambient') _playAmbient();
  else if (cat === 'tension') _playTension();
  else if (cat === 'kill')    _playKillSting();
  else if (cat === 'win')     _playWin();
}

/* ═══════════════════════════════════════════════════════
   INPUT
═══════════════════════════════════════════════════════ */
document.addEventListener('keydown', e => {
  const k = e.key;
  if (['ArrowUp','ArrowDown','ArrowLeft','ArrowRight',' ','Enter'].includes(k))
    e.preventDefault();

  _getAC();   // unlock AudioContext on first user gesture

  // Difficulty selection on start screen
  if (phase === 'start') {
    if (k === '1') { difficulty = 1; WIN_TIME = 180; return; }
    if (k === '2') { difficulty = 2; WIN_TIME = 300; return; }
    if (k === '3') { difficulty = 3; WIN_TIME = 600; return; }
  }

  if (k === ' ' || k === 'Enter') {
    if (phase === 'lore')  { phase = 'intro'; return; }
    if (phase === 'start') { startPlaying(); return; }
    if ((phase === 'over' || phase === 'win') && (phase !== 'win' || winT > 5000)) {
      introY = -40; introPhase = 0; introT = 0;
      phase  = 'intro'; return;
    }
  }

  if (!keysHeld[k] && phase === 'playing') {
    keysHeld[k]    = true;
    keyLastMove[k] = performance.now();
    handleKey(k);
  } else {
    keysHeld[k] = true;
  }
});

document.addEventListener('keyup', e => { delete keysHeld[e.key]; });

/* ═══════════════════════════════════════════════════════
   MAIN LOOP
═══════════════════════════════════════════════════════ */
let lastT = 0;
function loop(ts) {
  const dt = Math.min((ts - lastT)/1000, 0.05);
  lastT = ts;
  ctx.clearRect(0,0,W,H);
  _updateMusic();
  switch(phase) {
    case 'lore':    updateLore(dt);    drawLore(ts);    break;
    case 'intro':   updateIntro(dt);   drawIntro(ts);   break;
    case 'start':                       drawStart(ts);   break;
    case 'playing': updatePlaying(dt); drawPlaying(ts); break;
    case 'kill':    updateKill(dt);    drawKill(ts);    break;
    case 'over':                        drawOver(ts);    break;
    case 'win':     updateWin(dt);     drawWin(ts);     break;
  }
  requestAnimationFrame(loop);
}

/* ═══════════════════════════════════════════════════════
   INIT
═══════════════════════════════════════════════════════ */
ensureMaze(COLS + 8);
introY = -40;
requestAnimationFrame(ts => { lastT = ts; requestAnimationFrame(loop); });
</script>
</body>
</html>"""


@app.route('/')
def index():
    return GAME_HTML, 200, {'Content-Type': 'text/html; charset=utf-8'}


if __name__ == '__main__':
    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║       URETHANE — 无限迷宫  |  游戏服务器已启动      ║")
    print("╠══════════════════════════════════════════════════════╣")
    print("║  本机访问:  http://127.0.0.1:8080                   ║")
    print("║  外网访问:  http://<GCP 外部 IP>:8080               ║")
    print("║  按 Ctrl+C 停止                                     ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()
    app.run(host='0.0.0.0', port=8080, debug=False)
