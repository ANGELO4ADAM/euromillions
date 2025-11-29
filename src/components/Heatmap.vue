<template>
  <div class="card">
    <h3>Heatmap</h3>
    <p>Visualisation simplifiée des écarts.</p>
    <div class="heatmap-grid">
      <span v-for="cell in 20" :key="cell" class="heat-cell"></span>
    </div>
  </div>
</template>

<style scoped>
.heatmap-grid {
  display: grid;
  grid-template-columns: repeat(10, 1fr);
  gap: 6px;
  margin-top: 8px;
}

.heat-cell {
  height: 16px;
  border-radius: 4px;
  background: linear-gradient(135deg, #22d3ee, #6366f1);
  opacity: 0.7;
}
</style>
