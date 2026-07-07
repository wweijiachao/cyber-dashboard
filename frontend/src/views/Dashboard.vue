<template>
  <div class="glass-card">
    <!-- 头部 (保留原样) -->
    <div class="header">
      <div class="header-left">
        <span class="status-dot"></span>
        <h1 class="header-title">性能监控</h1>
      </div>
      <div class="header-connection-status">
        <div class="connection-status">
          <span class="dot" :class="connected ? 'online' : 'offline'"></span>
          {{ connected ? "已连接" : "断开重连中..." }}
        </div>
      </div>
    </div>

    <!-- 网格 -->
    <div class="dashboard-grid">
      <!-- 1. CPU 纯文本卡片 -->
      <div class="glass-card text-card">
        <div class="text-label">CPU 使用率</div>
        <div class="text-value">{{ cpuUsage }}<small>%</small></div>
      </div>

      <!-- 2. 内存 纯文本卡片 -->
      <div class="glass-card text-card">
        <div class="text-label">内存使用率</div>
        <div class="text-value">{{ memoryPercent }}<small>%</small></div>
      </div>

      <!-- 3. 内存详情 纯文本卡片 -->
      <div class="glass-card text-card">
        <div class="text-label">内存详情</div>
        <div class="text-value detail-font">
          <span>{{ memoryUsed }}</span> / {{ memoryTotal
          }}<small>GB</small>
        </div>
      </div>

      <!-- 4. 运行时间 纯文本卡片 -->
      <div class="glass-card text-card">
        <div class="text-label">系统运行时间</div>
        <div class="text-value uptime-font">{{ uptime }}</div>
      </div>

      

      <!-- 5. 历史趋势图 (保留) -->
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
import { ref, onMounted, onUnmounted } from "vue";
import * as echarts from "echarts";

const connected = ref(false);
const interval = ref(1);

const cpuUsage = ref(0);
const memoryPercent = ref(0);
const uptime = ref("--:--:--");
const memoryUsed = ref(0);
const memoryTotal = ref(0);

let ws = null;
let isDestroyed = false;

const connectWebSocket = () => {
  ws = new WebSocket("ws://localhost:8765");

  ws.onopen = () => {
    console.log("WebSocket 已连接");
    connected.value = true;
  };

  ws.onmessage = (messageEvent) => {
    const data = JSON.parse(messageEvent.data);
    uptime.value = data.boot_time;
    cpuUsage.value = data.cpu_usage;
    memoryPercent.value = data.memory_percent;
    memoryUsed.value = data.memory_used.toFixed(1);
    memoryTotal.value = data.memory_total.toFixed(1);
  };

  ws.onclose = () => {
    console.log("WebSocket 已断开");
    connected.value = false;
    if (!isDestroyed) {
      setTimeout(connectWebSocket, 2000);
    }
  };

  ws.onerror = (error) => {
    console.error("WebSocket 错误:", error);
  };
};

onMounted(() => {
  connectWebSocket();
});

onUnmounted(() => {
  isDestroyed = true;
  if (ws) {
    ws.close();
  }
});
</script>

<style scoped>
/* ==================== 基础与玻璃态 ==================== */
.glass-card {
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 24px; /* 稍微缩小圆角让纯文本更干练 */
  box-shadow:
    0 25px 50px -12px rgba(0, 0, 0, 0.8),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
  padding: 5px 24px;
  transition: all 0.25s ease;
}

.glass-card:hover {
  border-color: rgba(255, 255, 255, 0.1);
  box-shadow: 0 30px 60px -12px rgba(0, 0, 0, 0.9);
}

/* ==================== 头部控制台 ==================== */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2px;
  flex-wrap: wrap;
  gap: 16px;
  height: 52px;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 5px;
}
.header-connection-status {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.status-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 20px rgba(34, 197, 94, 0.5);
  animation: pulse-dot 1.8s infinite;
}
@keyframes pulse-dot {
  0%,
  100% {
    opacity: 0.6;
    transform: scale(0.95);
  }
  50% {
    opacity: 1;
    transform: scale(1.1);
  }
}

.header h1 {
  font-weight: 600;
  font-size: 26px;
  background: linear-gradient(135deg, #e0e7ff, #a5b4fc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.header-badge {
  background: rgba(255, 255, 255, 0.05);
  padding: 8px 16px;
  border-radius: 40px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  font-size: 14px;
  display: flex;
  gap: 10px;
}
.header-badge .label {
  color: #64748b;
}
.header-badge .value {
  color: #e2e8f0;
  font-weight: 500;
  font-variant-numeric: tabular-nums;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #94a3b8;
  background: rgba(255, 255, 255, 0.03);
  padding: 0px 16px;
  border-radius: 30px;
  border: 1px solid rgba(255, 255, 255, 0.04);
}
.connection-status .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.connection-status .dot.online {
  background: #22c55e;
  box-shadow: 0 0 12px rgba(34, 197, 94, 0.4);
}
.connection-status .dot.offline {
  background: #ef4444;
  box-shadow: 0 0 12px rgba(239, 68, 68, 0.3);
}

/* ==================== 网格系统 ==================== */
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 20px;
}

/* ==================== 极简文本卡片 ==================== */
.text-card {
  grid-column: span 3; /* 默认电脑端一行4个 */
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 28px 16px; /* 让卡片有点呼吸感 */
}

.text-label {
  color: #94a3b8;
  font-size: 15px;
  font-weight: 500;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
}

.text-value {
  font-size: 42px; /* 放大数字，极简风格的核心 */
  font-weight: 600;
  color: #f1f5f9;
  font-variant-numeric: tabular-nums;
  line-height: 1;
}

.text-value small {
  font-size: 20px;
  color: #64748b;
  margin-left: 4px;
  font-weight: 400;
}

/* 针对运行时间的等宽字体 */
.uptime-font {
  font-family: Consolas, Monaco, "Courier New", monospace;
  font-size: 36px;
  letter-spacing: 1px;
}

/* 针对内存详情的特定排版 */
.detail-font {
  font-size: 28px;
}
.highlight-used {
  color: #facc15; /* 已用内存高亮为黄色 */
}
.highlight-percent {
  font-size: 18px;
  color: #64748b;
  margin-left: 8px;
}

/* ==================== 趋势图卡片 ==================== */
.trend-card {
  grid-column: span 12;
}
.trend-chart {
  width: 100%;
  height: 200px;
}
.trend-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.trend-header h3 {
  color: #e2e8f0;
  font-weight: 500;
  font-size: 16px;
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

/* ==================== 响应式适配 ==================== */

/* 1. 手机竖屏 / 平板竖屏 */
@media (max-width: 768px) {
  .text-card {
    grid-column: span 6; /* 一行显示2个卡片 */
    padding: 20px 10px;
  }
  .text-value {
    font-size: 36px;
  }
  .uptime-font {
    font-size: 28px;
  }
  .detail-font {
    font-size: 24px;
  }
  .header {
    flex-direction: column;
    align-items: flex-start;
  }
}

/* 2. 手机横屏专属 (例如宽度 780px, 高度 < 400px) */
@media (max-width: 900px) and (orientation: landscape) {
  .dashboard-grid {
    gap: 12px;
  }

  .text-card {
    grid-column: span 3; /* 强制一行显示4个 */
    padding: 16px 8px; /* 极致压缩上下高度 */
  }

  .text-label {
    font-size: 13px;
    margin-bottom: 8px;
  }

  .text-value {
    font-size: 28px;
  }
  .text-value small {
    font-size: 14px;
  }
  .uptime-font {
    font-size: 22px;
  }
  .detail-font {
    font-size: 18px;
  }
  .highlight-percent {
    font-size: 14px;
    margin-left: 4px;
  }

  .trend-chart {
    height: 120px;
  } /* 压缩图表以防横屏溢出 */
}

.header-title {
  height: 32px;
  width: 108px;
}
</style>
