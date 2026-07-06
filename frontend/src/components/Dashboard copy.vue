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

// ---------- 响应式数据 ----------
const connected = ref(false);
const interval = ref(1); // 秒

const cpuUsage = ref(0);
const memoryPercent = ref(0);
const memoryUsed = ref(0);
const memoryTotal = ref(0);
const uptime = ref("00:00:00");

// 历史数据 (最多30个点)
const historyCpu = ref([]);
const historyMem = ref([]);
const historyTime = ref([]);

// DOM 引用
const cpuGauge = ref(null);
const memGauge = ref(null);
const trendChart = ref(null);

// ECharts 实例
let cpuChart = null;
let memChart = null;
let trend = null;

// WebSocket 对象
let ws = null;
let reconnectTimer = null;
let isManualClose = false;

// ---------- 初始化 ECharts ----------
function initGauges() {
  // CPU 仪表盘
  cpuChart = echarts.init(cpuGauge.value);
  cpuChart.setOption({
    series: [
      {
        type: "gauge",
        startAngle: 210,
        endAngle: -30,
        min: 0,
        max: 100,
        splitNumber: 4,
        radius: "85%",
        center: ["50%", "55%"],
        axisLine: {
          lineStyle: {
            width: 14,
            color: [[1, "#3b82f6"]],
          },
        },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        detail: { show: false },
        pointer: {
          show: false,
        },
        progress: {
          show: true,
          width: 14,
          itemStyle: {
            color: {
              type: "linear",
              x: 0,
              y: 0,
              x2: 1,
              y2: 0,
              colorStops: [
                { offset: 0, color: "#60a5fa" },
                { offset: 0.5, color: "#3b82f6" },
                { offset: 1, color: "#2563eb" },
              ],
            },
          },
        },
        data: [{ value: 0 }],
      },
    ],
  });

  // 内存仪表盘
  memChart = echarts.init(memGauge.value);
  memChart.setOption({
    series: [
      {
        type: "gauge",
        startAngle: 210,
        endAngle: -30,
        min: 0,
        max: 100,
        splitNumber: 4,
        radius: "85%",
        center: ["50%", "55%"],
        axisLine: {
          lineStyle: {
            width: 14,
            color: [[1, "#facc15"]],
          },
        },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        detail: { show: false },
        pointer: { show: false },
        progress: {
          show: true,
          width: 14,
          itemStyle: {
            color: {
              type: "linear",
              x: 0,
              y: 0,
              x2: 1,
              y2: 0,
              colorStops: [
                { offset: 0, color: "#fbbf24" },
                { offset: 0.5, color: "#f59e0b" },
                { offset: 1, color: "#d97706" },
              ],
            },
          },
        },
        data: [{ value: 0 }],
      },
    ],
  });

  // 趋势图
  trend = echarts.init(trendChart.value);
  trend.setOption({
    tooltip: {
      trigger: "axis"
    },
    grid: {
      left: 40,
      right: 16,
      top: 20,
      bottom: 28,
    },
    xAxis: {
      type: "category",
      data: [],
      axisLine: { lineStyle: { color: "rgba(255,255,255,0.06)" } },
      axisLabel: { color: "#64748b", fontSize: 10, interval: 4 },
      splitLine: { show: false },
    },
    yAxis: {
      type: "value",
      min: 0,
      max: 100,
      splitLine: {
        lineStyle: { color: "rgba(255,255,255,0.04)", type: "dashed" },
      },
      axisLabel: { color: "#64748b", fontSize: 10, formatter: "{value}%" },
    },
    series: [
      {
        name: "CPU",
        type: "line",
        smooth: true,
        symbol: "none",
        lineStyle: { width: 2.5, color: "#60a5fa" },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "rgba(96,165,250,0.25)" },
            { offset: 1, color: "rgba(96,165,250,0.01)" },
          ]),
        },
        data: [],
      },
      {
        name: "内存",
        type: "line",
        smooth: true,
        symbol: "none",
        lineStyle: { width: 2.5, color: "#facc15" },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "rgba(250,204,21,0.20)" },
            { offset: 1, color: "rgba(250,204,21,0.01)" },
          ]),
        },
        data: [],
      },
    ],
  });
}

// ---------- 更新 UI ----------
function updateUI(data) {
  cpuUsage.value = data.cpu_usage ?? 0;
  memoryPercent.value = data.memory_percent ?? 0;
  memoryUsed.value = data.memory_used ? data.memory_used.toFixed(1) : 0;
  memoryTotal.value = data.memory_total ? data.memory_total.toFixed(1) : 0;

  // 运行时间 (后端传来的是 HH:MM:SS)
  if (data.boot_time) {
    uptime.value = data.boot_time;
  }

  // 更新仪表盘
  if (cpuChart) {
    cpuChart.setOption({
      series: [{ data: [{ value: cpuUsage.value }] }],
    });
  }
  if (memChart) {
    memChart.setOption({
      series: [{ data: [{ value: memoryPercent.value }] }],
    });
  }

  // 更新历史趋势 (保留最近30个点)
  const now = new Date();
  const timeStr =
    now.getHours().toString().padStart(2, "0") +
    ":" +
    now.getMinutes().toString().padStart(2, "0") +
    ":" +
    now.getSeconds().toString().padStart(2, "0");

  historyCpu.value.push(cpuUsage.value);
  historyMem.value.push(memoryPercent.value);
  historyTime.value.push(timeStr);

  if (historyCpu.value.length > 30) {
    historyCpu.value.shift();
    historyMem.value.shift();
    historyTime.value.shift();
  }

  // 更新趋势图
  if (trend) {
    trend.setOption({
      xAxis: { data: historyTime.value.slice() },
      series: [
        { data: historyCpu.value.slice() },
        { data: historyMem.value.slice() },
      ],
    });
  }
}

// ---------- WebSocket 连接 ----------
function connectWebSocket() {
  if (
    ws &&
    (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)
  ) {
    return;
  }

  try {
    ws = new WebSocket("ws://localhost:8765");
    ws.onopen = () => {
      console.log("WebSocket 已连接");
      connected.value = true;
      isManualClose = false;
      if (reconnectTimer) {
        clearTimeout(reconnectTimer);
        reconnectTimer = null;
      }
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        updateUI(data);
      } catch (e) {
        console.warn("解析数据失败", e);
      }
    };

    ws.onclose = () => {
      console.log("WebSocket 已断开");
      connected.value = false;
      if (!isManualClose) {
        // 自动重连
        if (reconnectTimer) clearTimeout(reconnectTimer);
        reconnectTimer = setTimeout(() => {
          connectWebSocket();
        }, 2000);
      }
    };

    ws.onerror = (err) => {
      console.error("WebSocket 错误", err);
      ws.close();
    };
  } catch (e) {
    console.error("连接失败", e);
    connected.value = false;
    if (!isManualClose) {
      reconnectTimer = setTimeout(() => {
        connectWebSocket();
      }, 3000);
    }
  }
}

// ---------- 窗口自适应 ----------
function resizeCharts() {
  cpuChart?.resize();
  memChart?.resize();
  trend?.resize();
}

// ---------- 生命周期 ----------
onMounted(() => {
  nextTick(() => {
    initGauges();
    connectWebSocket();
    window.addEventListener("resize", resizeCharts);
  });
});

onBeforeUnmount(() => {
  isManualClose = true;
  if (ws) {
    ws.close();
    ws = null;
  }
  if (reconnectTimer) {
    clearTimeout(reconnectTimer);
    reconnectTimer = null;
  }
  window.removeEventListener("resize", resizeCharts);
  cpuChart?.dispose();
  memChart?.dispose();
  trend?.dispose();
});

// 监听连接状态变化，更新UI
watch(connected, (val) => {
  // 可以做一些额外反馈
});
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
  font-size: 44px;
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
