<template>
  <div class="max-w-5xl mx-auto">
    <h2 class="text-2xl font-bold text-white mb-4 text-center">公式推导</h2>

    <!-- 模式切换 -->
    <div class="flex justify-center gap-2 mb-6">
      <button
        v-for="mode in modes"
        :key="mode.id"
        @click="switchMode(mode.id)"
        :class="['px-5 py-2 rounded-lg font-medium transition', currentMode === mode.id ? 'bg-amber-600 text-white' : 'bg-slate-700 text-gray-300 hover:bg-slate-600']"
      >{{ mode.name }}</button>
    </div>

    <!-- 等式显示 -->
    <div class="text-center mb-6">
      <div class="text-3xl font-bold text-amber-400">{{ currentModeInfo.formula }}</div>
      <div class="text-sm text-gray-400 mt-1">{{ currentModeInfo.description }}</div>
    </div>

    <!-- 演示区域 -->
    <div class="grid grid-cols-2 gap-6 mb-6">
      <!-- 左侧：初始区 -->
      <div class="bg-slate-800 rounded-xl p-4 min-h-[280px]">
        <div class="text-center text-gray-400 text-sm mb-3">{{ currentModeInfo.leftLabel }}</div>
        <div class="flex flex-wrap gap-3 justify-center items-start">
          <!-- 直接乘法 / 展开模式：显示篮子 -->
          <template v-if="currentMode === 'multiply' || currentMode === 'expand'">
            <div
              v-for="i in basketCount"
              :key="'basket-' + i"
              class="basket"
              :class="{ 'basket-opened': openedBaskets.includes(i) }"
            >
              <div class="basket-handle"></div>
              <div class="basket-body">
                <template v-if="currentMode === 'multiply'">
                  <div class="flex flex-wrap gap-1 justify-center max-w-[100px]">
                    <span v-for="n in chickenPerBasket" :key="n" class="animal">🐔</span>
                  </div>
                </template>
                <template v-else>
                  <div class="flex flex-wrap gap-1 justify-center max-w-[100px]">
                    <span v-for="n in chickenPerBasket" :key="'c'+n" class="animal">🐔</span>
                  </div>
                  <div class="flex flex-wrap gap-1 justify-center max-w-[100px]">
                    <span v-for="n in duckPerBasket" :key="'d'+n" class="animal">🦆</span>
                  </div>
                  <div class="text-xs text-amber-300 mt-1">({{ chickenPerBasket }}+{{ duckPerBasket }})</div>
                </template>
              </div>
            </div>
          </template>

          <!-- 合并模式：显示散放动物 -->
          <template v-if="currentMode === 'merge'">
            <div class="flex flex-col gap-3 w-full">
              <!-- 鸡组 -->
              <div class="flex flex-wrap gap-3 justify-center">
                <div
                  v-for="i in groupCount"
                  :key="'chicken-group-' + i"
                  class="animal-group"
                  :class="{ 'animal-group-merged': mergedGroups.includes(i) }"
                >
                  <span v-for="n in chickenPerBasket" :key="n" class="animal">🐔</span>
                  <div class="text-xs text-center text-amber-300 mt-1">第{{ i }}组</div>
                </div>
              </div>
              <!-- 鸭组 -->
              <div class="flex flex-wrap gap-3 justify-center">
                <div
                  v-for="i in groupCount"
                  :key="'duck-group-' + i"
                  class="animal-group"
                  :class="{ 'animal-group-merged': mergedGroups.includes(i) }"
                >
                  <span v-for="n in duckPerBasket" :key="n" class="animal">🦆</span>
                  <div class="text-xs text-center text-amber-300 mt-1">第{{ i }}组</div>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>

      <!-- 右侧：结果区 -->
      <div class="bg-slate-800 rounded-xl p-4 min-h-[280px]">
        <div class="text-center text-gray-400 text-sm mb-3">{{ currentModeInfo.rightLabel }}</div>
        <div class="flex flex-wrap gap-3 justify-center items-start">
          <!-- 直接乘法 / 展开模式：展开后散放动物 -->
          <template v-if="currentMode === 'multiply' || currentMode === 'expand'">
            <TransitionGroup name="animal" tag="div" class="flex flex-col gap-3">
              <!-- 展开模式：鸡和鸭各自分组显示（3×2 + 3×5） -->
              <template v-if="currentMode === 'expand'">
                <!-- 鸡组：openedBaskets.length 组，每组 chickenPerBasket 只 -->
                <div v-if="openedBaskets.length > 0" key="chicken-block" class="w-full">
                  <div class="text-xs text-amber-300 mb-1 text-center">
                    🐔 {{ openedBaskets.length }}×{{ chickenPerBasket }} = {{ totalChickens }}
                  </div>
                  <div class="flex flex-wrap gap-2 justify-center">
                    <div v-for="b in openedBaskets" :key="'cg-'+b" class="basket-group">
                      <div class="flex flex-wrap gap-1 justify-center max-w-[80px]">
                        <span v-for="n in chickenPerBasket" :key="'cc'+b+'-'+n" class="animal">🐔</span>
                      </div>
                      <div class="text-xs text-amber-300 mt-1 text-center">第{{ b }}组</div>
                    </div>
                  </div>
                </div>
                <!-- 加号分隔 -->
                <div v-if="openedBaskets.length > 0" key="plus-sign" class="w-full text-center text-2xl font-bold text-green-400">+</div>
                <!-- 鸭组：openedBaskets.length 组，每组 duckPerBasket 只 -->
                <div v-if="openedBaskets.length > 0" key="duck-block" class="w-full">
                  <div class="text-xs text-amber-300 mb-1 text-center">
                    🦆 {{ openedBaskets.length }}×{{ duckPerBasket }} = {{ totalDucks }}
                  </div>
                  <div class="flex flex-wrap gap-2 justify-center">
                    <div v-for="b in openedBaskets" :key="'dg-'+b" class="basket-group">
                      <div class="flex flex-wrap gap-1 justify-center max-w-[80px]">
                        <span v-for="n in duckPerBasket" :key="'dd'+b+'-'+n" class="animal">🦆</span>
                      </div>
                      <div class="text-xs text-amber-300 mt-1 text-center">第{{ b }}组</div>
                    </div>
                  </div>
                </div>
              </template>
              <!-- 直接乘法：按篮子分组显示 -->
              <template v-else>
                <div v-if="openedBaskets.length > 0" key="basket-groups" class="flex flex-wrap gap-3 justify-center">
                  <div v-for="b in openedBaskets" :key="'bg-'+b" class="basket-group">
                    <div class="flex flex-wrap gap-1 justify-center max-w-[80px]">
                      <span v-for="n in chickenPerBasket" :key="'bc'+b+'-'+n" class="animal">🐔</span>
                    </div>
                    <div class="text-xs text-amber-300 mt-1 text-center">第{{ b }}篮</div>
                  </div>
                </div>
                <div v-if="openedBaskets.length > 0" key="chicken-summary" class="w-full text-center text-sm text-amber-300">
                  🐔 {{ chickenPerBasket }} × {{ openedBaskets.length }} = {{ totalChickens }}
                </div>
              </template>
            </TransitionGroup>
          </template>

          <!-- 合并模式：合并后显示篮子 -->
          <template v-if="currentMode === 'merge'">
            <div
              v-for="i in mergedGroups.length"
              :key="'merged-basket-' + i"
              class="basket basket-opened"
            >
              <div class="basket-handle"></div>
              <div class="basket-body">
                <div class="flex flex-wrap gap-1 justify-center max-w-[100px]">
                  <span v-for="n in chickenPerBasket" :key="'c'+n" class="animal">🐔</span>
                </div>
                <div class="flex flex-wrap gap-1 justify-center max-w-[100px]">
                  <span v-for="n in duckPerBasket" :key="'d'+n" class="animal">🦆</span>
                </div>
                <div class="text-xs text-amber-300 mt-1">({{ chickenPerBasket }}+{{ duckPerBasket }})</div>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- 等式变化 -->
    <div class="bg-slate-800 rounded-xl p-4 mb-6 text-center">
      <Transition name="expr" mode="out-in">
        <div :key="equationText" class="text-xl font-mono font-bold text-green-400">
          {{ equationText }}
        </div>
      </Transition>
    </div>

    <!-- 操作面板 -->
    <div class="bg-slate-800 rounded-xl p-4">
      <!-- 数量选择 -->
      <div class="flex flex-wrap items-center justify-center gap-6 mb-4">
        <div v-if="currentMode === 'merge'" class="flex items-center gap-2">
          <span class="text-gray-300">组数：</span>
          <input v-model.number="groupCount" type="number" min="1" max="9" class="w-16 px-2 py-1 rounded bg-slate-700 text-white text-center" />
        </div>
        <div v-else class="flex items-center gap-2">
          <span class="text-gray-300">篮子数量：</span>
          <input v-model.number="basketCount" type="number" min="1" max="9" class="w-16 px-2 py-1 rounded bg-slate-700 text-white text-center" />
        </div>
        <div class="flex items-center gap-2">
          <span class="text-gray-300">🐔 每篮：</span>
          <input v-model.number="chickenPerBasket" type="number" min="1" max="9" class="w-16 px-2 py-1 rounded bg-slate-700 text-white text-center" />
        </div>
        <div v-if="currentMode !== 'multiply'" class="flex items-center gap-2">
          <span class="text-gray-300">🦆 每篮：</span>
          <input v-model.number="duckPerBasket" type="number" min="1" max="9" class="w-16 px-2 py-1 rounded bg-slate-700 text-white text-center" />
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="flex justify-center gap-4">
        <button
          @click="playAnimation"
          :disabled="animating"
          :class="['px-6 py-2 rounded-lg font-medium transition', animating ? 'bg-gray-600 text-gray-400 cursor-not-allowed' : 'bg-amber-600 text-white hover:bg-amber-700']"
        >
          {{ animating ? '演示中...' : buttonText }}
        </button>
        <button
          @click="reset"
          class="px-6 py-2 bg-slate-600 text-white rounded-lg hover:bg-slate-500 transition"
        >
          重置
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const currentMode = ref('multiply')

const modes = [
  {
    id: 'multiply',
    name: '直接乘法',
    formula: '3 × 2 = 6',
    description: '几个篮子，每个装同样数量的动物',
    leftLabel: '篮子区',
    rightLabel: '倒出来数'
  },
  {
    id: 'expand',
    name: '展开（去括号）',
    formula: '3 × (2 + 5) = 3×2 + 3×5',
    description: '把篮子里的动物倒出来分类统计',
    leftLabel: '篮子区（每个有鸡有鸭）',
    rightLabel: '倒出来分类数'
  },
  {
    id: 'merge',
    name: '合并（提公因数）',
    formula: '3×2 + 3×5 = 3 × (2 + 5)',
    description: '把散放的动物装进篮子',
    leftLabel: '散放区（无篮子）',
    rightLabel: '装进篮子'
  }
]

const currentModeInfo = computed(() => modes.find(m => m.id === currentMode.value))

// 参数
const basketCount = ref(3)
const groupCount = ref(3)
const chickenPerBasket = ref(2)
const duckPerBasket = ref(5)

// 动画状态
const animating = ref(false)
const openedBaskets = ref([])
const mergedGroups = ref([])

const totalChickens = computed(() => chickenPerBasket.value * openedBaskets.value.length)
const totalDucks = computed(() => duckPerBasket.value * openedBaskets.value.length)

const buttonText = computed(() => {
  switch (currentMode.value) {
    case 'multiply': return '倒出来'
    case 'expand': return '展开'
    case 'merge': return '合并装篮'
    default: return '开始'
  }
})

const equationText = computed(() => {
  const count = currentMode.value === 'merge' ? groupCount.value : basketCount.value
  const c = chickenPerBasket.value
  const d = duckPerBasket.value

  if (currentMode.value === 'multiply') {
    if (openedBaskets.value.length === 0) return `${count} × ${c} = ?`
    return `${count} × ${c} = ${count * c}`
  }

  if (currentMode.value === 'expand') {
    if (openedBaskets.value.length === 0) return `${count} × (${c} + ${d}) = ?`
    if (openedBaskets.value.length < count) return `${count} × (${c} + ${d}) = ${count}×${c} + ${count}×${d} = ?`
    return `${count} × (${c} + ${d}) = ${count}×${c} + ${count}×${d} = ${count * c} + ${count * d} = ${count * (c + d)}`
  }

  if (currentMode.value === 'merge') {
    if (mergedGroups.value.length === 0) return `${count}×${c} + ${count}×${d} = ?`
    if (mergedGroups.value.length < count) return `${count}×${c} + ${count}×${d} = ${count} × (${c} + ${d}) = ?`
    return `${count}×${c} + ${count}×${d} = ${count} × (${c} + ${d}) = ${count * (c + d)}`
  }

  return ''
})

function switchMode(mode) {
  currentMode.value = mode
  reset()
}

function reset() {
  openedBaskets.value = []
  mergedGroups.value = []
  animating.value = false
}

async function playAnimation() {
  if (animating.value) return
  reset()
  animating.value = true

  if (currentMode.value === 'merge') {
    // 合并模式：逐组装篮
    const count = groupCount.value
    for (let i = 1; i <= count; i++) {
      await sleep(600)
      mergedGroups.value = [...mergedGroups.value, i]
    }
  } else {
    // 直接乘法 / 展开模式：逐个倒出
    const count = basketCount.value
    for (let i = 1; i <= count; i++) {
      await sleep(500)
      openedBaskets.value = [...openedBaskets.value, i]
    }
  }

  animating.value = false
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}
</script>

<style scoped>
.basket {
  min-width: 90px;
  max-width: 120px;
  min-height: 70px;
  background: linear-gradient(135deg, #92400e, #b45309);
  border-radius: 8px;
  padding: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  transition: all 0.4s ease;
  overflow: hidden;
}
.basket-handle {
  width: 40px;
  height: 12px;
  border: 3px solid #92400e;
  border-bottom: none;
  border-radius: 20px 20px 0 0;
  position: absolute;
  top: -10px;
  background: transparent;
}
.basket-body {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  flex-wrap: wrap;
  justify-content: center;
}
.basket-opened {
  opacity: 0.4;
  transform: scale(0.95);
}

.animal {
  font-size: 16px;
  display: inline-block;
  transition: all 0.3s ease;
}

.animal-group {
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  border: 1px dashed rgba(255, 255, 255, 0.2);
  transition: all 0.4s ease;
}
.animal-group-merged {
  opacity: 0.3;
  transform: scale(0.9);
}

.basket-group {
  padding: 8px 10px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  border: 1px dashed rgba(255, 255, 255, 0.2);
}

.animal-enter-active {
  transition: all 0.5s ease;
}
.animal-enter-from {
  opacity: 0;
  transform: scale(0.3) translateY(-20px);
}

.expr-enter-active,
.expr-leave-active {
  transition: all 0.4s ease;
}
.expr-enter-from {
  opacity: 0;
  transform: scale(0.8) translateY(-10px);
}
.expr-leave-to {
  opacity: 0;
  transform: scale(0.8) translateY(10px);
}
</style>
