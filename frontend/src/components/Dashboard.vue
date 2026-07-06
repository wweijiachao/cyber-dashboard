<template>
  <div class="glass-card">
    <!-- 头部 -->
    <div class="header">
      <div class="header-left">
        <span class="status-dot"></span>
        <h1>⚡ 性能监控</h1>
      </div>
      <div class="header-connection-status">
        <div class="connection-status">
          <span class="dot" :class="connected ? 'online' : 'offline'"></span>
          {{ connected ? "已连接" : "断开重连中..." }}
        </div>
        <div class="header-badge">
          <span class="label">🔄 更新</span>
          <span class="value">{{ interval }}s</span>
        </div>
      </div>
    </div>

    <!-- 网格 -->
    <div class="dashboard-grid">
      <!-- CPU 仪表盘 -->
      <div class="glass-card gauge-card">
        <div class="gauge-wrapper">
          <div ref="cpuGauge" class="gauge-chart"></div>
          <div class="gauge-label">CPU 使用率</div>
          <div class="gauge-value">{{ cpuUsage }}<small>%</small></div>
        </div>
      </div>

      <!-- 内存仪表盘 -->
      <div class="glass-card gauge-card">
        <div class="gauge-wrapper">
          <div ref="memGauge" class="gauge-chart"></div>
          <div class="gauge-label">内存使用率</div>
          <div class="gauge-value">{{ memoryPercent }}<small>%</small></div>
        </div>
      </div>

      <!-- 运行时间 -->
      <div class="glass-card uptime-card">
        <div class="uptime-icon">⏱️</div>
        <div class="uptime-label">系统运行时间</div>
        <div class="uptime-display">
          <span class="time">{{ uptime }}</span>
          <span class="unit">h</span>
        </div>
        <div class="divider"></div>
        <div class="time-status">
          <span>🟢 活跃</span>
          <span>📊 实时</span>
        </div>
      </div>

      <!-- 内存详情 -->
      <div class="glass-card memory-detail-card">
        <div class="memory-title">
          <span class="memory-title-emoji">🧠</span>
          <span class="memory-title-word">内存详情</span>
        </div>
        <div class="memory-stats">
          <div class="memory-item">
            <span class="mem-label">已用</span>
            <span class="mem-value used">{{ memoryUsed }} GB</span>
          </div>
          <div class="memory-item">
            <span class="mem-label">总计</span>
            <span class="mem-value total">{{ memoryTotal }} GB</span>
          </div>
          <div class="memory-item">
            <span class="mem-label">使用率</span>
            <span class="mem-value" style="color: #facc15"
              >{{ memoryPercent }} %</span
            >
          </div>
        </div>
      </div>

      <!-- 历史趋势 -->
      <div class="glass-card trend-card">
        <div class="trend-header">
          <h3>📈 实时趋势 (最近 30 秒)</h3>
          <div class="legend">
            <span class="legend-cpu">CPU</span>
            <span class="legend-memory">内存</span>
          </div>
        </div>
        <div ref="trendChart" class="trend-chart"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from "vue";
import * as echarts from "echarts";

const connected = ref(false); // 是否连接
const interval = ref(1); // 更新间隔，单位秒

const cpuUsage = ref(0);
const memoryPercent = ref(0);
const uptime = ref("--:--:--");
const memoryUsed = ref(0);
const memoryTotal = ref(0);

let ws = null;  // WebSocket 实例

function connectWebSocket() {
  // 创建 WebSocket 连接
  ws = new WebSocket("ws://localhost:8765");

  ws.onopen = () => {
    console.log("WebSocket 已连接");
    connected.value = true;
  }
}


</script>

<style scoped>
/* 玻璃态卡片设计 */
.glass-card {
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 32px;
  box-shadow:
    0 25px 50px -12px rgba(0, 0, 0, 0.8),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
  padding: 28px 30px;
  transition: all 0.25s ease;

  padding-bottom: 18px;
}

.glass-card:hover {
  border-color: rgba(255, 255, 255, 0.1);
  box-shadow: 0 30px 60px -12px rgba(0, 0, 0, 0.9);
}

/* 头部 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
  flex-wrap: wrap;
  gap: 16px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.status-dot {
  display: inline-block;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 20px rgba(34, 197, 94, 0.5);
  animation: pulse-dot 1.8s infinite;
}

@keyframes pulse-dot {
  0% {
    opacity: 0.6;
    transform: scale(0.95);
  }

  50% {
    opacity: 1;
    transform: scale(1.1);
  }

  100% {
    opacity: 0.6;
    transform: scale(0.95);
  }
}

.header h1 {
  font-weight: 600;
  font-size: 26px;
  letter-spacing: -0.3px;
  color: #f0f2f8;
  background: linear-gradient(135deg, #e0e7ff, #a5b4fc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-badge {
  background: rgba(255, 255, 255, 0.05);
  padding: 10px 20px;
  border-radius: 40px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  color: #94a3b8;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  letter-spacing: 0.2px;
}

.header-badge .label {
  color: #64748b;
}

.header-badge .value {
  color: #e2e8f0;
  font-weight: 500;
  font-variant-numeric: tabular-nums;
}

/* 网格布局 */
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 24px;
}

/* CPU & 内存 仪表盘卡片 */
.gauge-card {
  grid-column: span 3;
}

.gauge-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  width: 100%;
}

.gauge-chart {
  width: 100%;
  height: 180px;
}

.gauge-label {
  color: #94a3b8;
  font-size: 15px;
  font-weight: 500;
  letter-spacing: 0.3px;
  margin-top: -6px;
  text-align: center;
}

.gauge-value {
  font-size: 32px;
  font-weight: 600;
  color: #f1f5f9;
  letter-spacing: -0.5px;
  margin-top: 4px;
}

.gauge-value small {
  font-size: 16px;
  font-weight: 400;
  color: #64748b;
  margin-left: 2px;
}

/* 运行时间卡片 */
.uptime-card {
  grid-column: span 3;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.uptime-display {
  display: flex;
  align-items: baseline;
  gap: 6px;
  margin: 6px 0 4px 0;
}

.uptime-display .time {
  font-family: Consolas, Monaco, "Courier New", monospace;
  font-size: 36px;
  font-weight: 600;
  color: #f1f5f9;
  letter-spacing: 1px;
  font-variant-numeric: tabular-nums;
}

.uptime-display .unit {
  font-size: 18px;
  color: #64748b;
  margin-left: 4px;
}

.uptime-label {
  color: #94a3b8;
  font-size: 14px;
  letter-spacing: 0.3px;
}

.uptime-icon {
  font-size: 28px;
  margin-bottom: 4px;
  opacity: 0.7;
}

/* 内存详情卡片 */
.memory-detail-card {
  grid-column: span 3;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.memory-stats {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 8px;
}

.memory-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

.memory-item:last-child {
  border-bottom: none;
}

.memory-item .mem-label {
  color: #94a3b8;
  font-size: 14px;
}

.memory-item .mem-value {
  color: #e2e8f0;
  font-weight: 500;
  font-size: 15px;
  font-variant-numeric: tabular-nums;
}

.memory-item .mem-value.used {
  color: #facc15;
}

.memory-item .mem-value.total {
  color: #60a5fa;
}

/* 历史趋势图卡片 */
.trend-card {
  grid-column: span 12;
  margin-top: 4px;
}

.trend-chart {
  width: 100%;
  height: 200px;
}

.trend-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.trend-header h3 {
  color: #e2e8f0;
  font-weight: 500;
  font-size: 16px;
  letter-spacing: 0.2px;
}

.trend-header .legend {
  display: flex;
  gap: 20px;
  color: #94a3b8;
  font-size: 13px;
}

.trend-header .legend span::before {
  content: "●";
  margin-right: 6px;
  font-size: 12px;
}

.legend-cpu::before {
  color: #60a5fa;
}

.legend-memory::before {
  color: #facc15;
}

/* 连接状态 */
.connection-status {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #94a3b8;
  background: rgba(255, 255, 255, 0.03);
  padding: 6px 16px 6px 12px;
  border-radius: 30px;
  border: 1px solid rgba(255, 255, 255, 0.04);
}

.connection-status .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.connection-status .dot.online {
  background: #22c55e;
  box-shadow: 0 0 12px rgba(34, 197, 94, 0.4);
}

.connection-status .dot.offline {
  background: #ef4444;
  box-shadow: 0 0 12px rgba(239, 68, 68, 0.3);
}

/* 响应式 */
@media (max-width: 1024px) {
  .gauge-card {
    grid-column: span 6;
  }

  .uptime-card {
    grid-column: span 6;
  }

  .memory-detail-card {
    grid-column: span 12;
  }
}

@media (max-width: 640px) {
  .gauge-card {
    grid-column: span 12;
  }

  .uptime-card {
    grid-column: span 12;
  }

  .header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-badge {
    width: 100%;
    justify-content: space-between;
  }

  .trend-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .glass-card {
    padding: 20px;
  }

  .uptime-display .time {
    font-size: 32px;
  }
}

/* 小美化 */
.glow-text {
  text-shadow: 0 0 40px rgba(96, 165, 250, 0.08);
}

.divider {
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.06),
    transparent
  );
  margin: 6px 0 12px 0;
}

/* 拆分行内样式 */
.header-connection-status {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}
.time-status {
  color: #64748b;
  font-size: 14px;
  display: flex;
  gap: 16px;
  margin-top: 4px;
}
.memory-title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}
.memory-title-emoji {
  font-size: 22px;
}
.memory-title-word {
  color: #e2e8f0;
  font-weight: 500;
}
</style>
