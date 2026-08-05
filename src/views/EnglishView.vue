<template>
  <div>
    <!-- 子模块导航 -->
    <nav class="bg-white/5 backdrop-blur-md border-b border-white/10">
      <div class="max-w-7xl mx-auto px-4">
        <div class="flex items-center justify-end h-12">
          <div class="flex items-center space-x-1">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              @click="currentTab = tab.id"
              :class="['nav-link text-white font-medium', currentTab === tab.id ? 'active' : '']"
            >
              {{ tab.name }}
            </button>
          </div>
        </div>
      </div>
    </nav>

    <main class="max-w-7xl mx-auto px-4 py-6">
      <!-- 模块1：音节拆分演示 -->
      <section v-if="currentTab === 'split'" class="max-w-4xl mx-auto">
        <h2 class="text-2xl font-bold text-white mb-2 text-center">音节拆分演示</h2>
        <p class="text-gray-400 text-sm text-center mb-6">基于自然拼读规则拆分，每个音节内部分字母段，元音高亮</p>

        <div class="flex justify-center gap-2 mb-6">
          <input
            v-model="wordInput"
            @keyup.enter="splitWord"
            placeholder="输入英文单词，如 football"
            class="px-4 py-2 rounded-lg bg-slate-700 text-white w-72 text-center lowercase"
          />
          <button @click="splitWord" class="px-6 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition">拆分</button>
        </div>

        <!-- 拆分结果 -->
        <div v-if="syllableResult.length > 0" class="bg-slate-800 rounded-xl p-6 mb-6">
          <div class="flex flex-wrap gap-4 justify-center items-start mb-4">
            <div
              v-for="(syl, idx) in syllableResult"
              :key="idx"
              class="syllable-card"
              :style="{ borderColor: syllableColors[idx % syllableColors.length] }"
            >
              <!-- 字母段 -->
              <div class="flex items-center gap-1 justify-center mb-2">
                <span
                  v-for="(seg, sidx) in syl.segments"
                  :key="sidx"
                  class="grapheme-seg"
                  :class="[seg.type, { 'double-consonant': seg.isDouble }]"
                  :title="seg.rule"
                >{{ seg.text }}</span>
              </div>
              <!-- 音节类型徽章 -->
              <div class="text-xs text-amber-300 text-center mb-1 font-medium">{{ syl.type }}</div>
              <!-- 段规则标注 -->
              <div class="flex flex-wrap gap-1 justify-center">
                <span
                  v-for="(seg, sidx) in syl.segments"
                  :key="'r'+sidx"
                  class="text-[10px] text-gray-500 min-w-[28px] text-center"
                >{{ seg.rule }}</span>
              </div>
            </div>
          </div>
          <div class="text-center text-gray-400 text-sm">
            共 <span class="text-amber-400 font-bold text-lg">{{ syllableResult.length }}</span> 个音节
          </div>
        </div>

        <!-- 示例单词 -->
        <div class="bg-slate-800 rounded-xl p-4">
          <div class="text-gray-300 text-sm mb-2">试试这些单词：</div>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="w in exampleWords"
              :key="w"
              @click="wordInput = w; splitWord()"
              class="px-3 py-1 bg-slate-700 text-white rounded hover:bg-slate-600 transition text-sm"
            >{{ w }}</button>
          </div>
        </div>
      </section>

      <!-- 模块2：6种音节类型教学 -->
      <section v-else-if="currentTab === 'types'" class="max-w-5xl mx-auto">
        <h2 class="text-2xl font-bold text-white mb-2 text-center">6 种基本音节类型</h2>
        <p class="text-gray-400 text-sm text-center mb-6">基于自然拼读规则判定</p>

        <!-- 实时判型 -->
        <div class="bg-slate-800 rounded-xl p-6 mb-6">
          <div class="flex justify-center gap-2 mb-4">
            <input
              v-model="typeInput"
              @input="detectType"
              placeholder="输入单词，判定音节类型"
              class="px-4 py-2 rounded-lg bg-slate-700 text-white w-64 text-center lowercase"
            />
          </div>
          <div v-if="typeResult" class="text-center">
            <div class="text-3xl font-bold text-amber-400 mb-2">{{ typeResult.word }}</div>
            <div class="flex flex-wrap gap-2 justify-center">
              <span
                v-for="(t, i) in typeResult.types"
                :key="i"
                class="px-3 py-1 bg-amber-600 text-white rounded-full text-sm"
              >{{ t }}</span>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div
            v-for="(t, idx) in syllableTypes"
            :key="t.name"
            class="bg-slate-800 rounded-xl p-5 border-l-4"
            :style="{ borderLeftColor: syllableColors[idx % syllableColors.length] }"
          >
            <div class="flex items-baseline justify-between mb-2">
              <h3 class="text-lg font-bold text-white">{{ idx + 1 }}. {{ t.name }}</h3>
              <span class="text-xs text-gray-400">{{ t.pattern }}</span>
            </div>
            <p class="text-gray-300 text-sm mb-3">{{ t.rule }}</p>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="ex in t.examples"
                :key="ex"
                @click="typeInput = ex; detectType()"
                class="px-2 py-1 bg-slate-700 text-amber-300 rounded text-sm font-mono cursor-pointer hover:bg-slate-600"
              >{{ ex }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 模块3：自然拼读发音参考 -->
      <section v-else-if="currentTab === 'pronounce'" class="max-w-5xl mx-auto">
        <h2 class="text-2xl font-bold text-white mb-2 text-center">自然拼读发音参考</h2>
        <p class="text-gray-400 text-sm text-center mb-6">按音节模式分组，点击示例词听发音</p>

        <!-- 搜索框 -->
        <div class="max-w-xl mx-auto mb-6 relative">
          <input
            v-model="searchPattern"
            placeholder="搜索音节模式或示例词，如 ai、a_e、cat"
            class="w-full px-4 py-2 pl-10 rounded-lg bg-slate-700 text-white placeholder-gray-400 border border-slate-600 focus:border-amber-500 focus:outline-none transition"
          />
          <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">🔍</span>
          <button
            v-if="searchPattern"
            @click="searchPattern = ''"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white"
            title="清除"
          >✕</button>
        </div>

        <div v-if="filteredPronounceGroups.length === 0" class="text-center text-gray-400 py-10">
          未找到匹配「{{ searchPattern }}」的音节模式
        </div>

        <div v-else class="space-y-5">
          <div
            v-for="(group, gidx) in filteredPronounceGroups"
            :key="group.name"
            :ref="el => { if (searchPattern && gidx === 0) firstMatchRef = el }"
            class="bg-slate-800 rounded-xl p-5 border-l-4 scroll-mt-4"
            :style="{ borderLeftColor: syllableColors[gidx % syllableColors.length] }"
          >
            <div class="flex items-baseline justify-between mb-3">
              <h3 class="text-lg font-bold text-white">{{ group.name }}</h3>
              <span class="text-xs text-gray-400">{{ group.hint }}</span>
            </div>
            <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
              <button
                v-for="item in group.items"
                :key="item.pattern"
                @click="speak(item.word, 0.8)"
                class="pronounce-item"
                :class="{ 'pronounce-item-highlighted': isItemMatch(item) }"
                :title="`点击听 ${item.word} 发音`"
              >
                <div class="text-amber-400 font-bold text-lg">{{ item.pattern }}</div>
                <div class="text-gray-300 text-sm">{{ item.word }}</div>
                <div class="text-xs text-gray-500 mt-1">🔊</div>
              </button>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'

const currentTab = ref('split')
const tabs = [
  { id: 'split', name: '音节拆分' },
  { id: 'types', name: '音节类型' },
  { id: 'pronounce', name: '音节发音' }
]

const syllableColors = [
  '#fbbf24',
  '#60a5fa',
  '#a78bfa',
  '#34d399',
  '#f87171',
  '#f472b6'
]

// ============ 自然拼读规则字典 ============
const VOWELS = 'aeiouy'

// 元音组合（一个音）
const VOWEL_TEAMS = [
  'igh', 'eigh', 'aigh', 'air', 'ear', 'eer', 'oor', 'our', 'oar',
  'ai', 'ay', 'ea', 'ee', 'ey', 'ie', 'oa', 'oe', 'oo', 'ou', 'ow', 'ue', 'ui', 'oi', 'oy', 'au', 'aw', 'eu', 'ew', 'ei'
]

// 辅音二合（1个音，不拆）
const CONSONANT_DIGRAPHS = ['tch', 'ch', 'sh', 'th', 'ph', 'wh', 'ck', 'ng', 'qu', 'wr', 'kn', 'gn', 'mb', 'gh']

// 辅音簇（多音连读，跨音节时仍可分）
const CONSONANT_BLENDS = ['scr', 'spr', 'spl', 'str', 'bl', 'br', 'cl', 'cr', 'dr', 'fl', 'fr', 'gl', 'gr', 'pl', 'pr', 'tr', 'sp', 'st', 'sk', 'sm', 'sn', 'sw', 'tw']

// 双辅音（相同字母双写，发单音）
const DOUBLE_CONSONANTS = ['ll', 'ss', 'tt', 'nn', 'pp', 'dd', 'gg', 'bb', 'mm', 'ff', 'rr']

// ============ 音节拆分核心算法 ============

// 查找元音核（连续元音字母组 + 可能的 r）
function findVowelCores(w) {
  const cores = []
  let i = 0
  while (i < w.length) {
    if (VOWELS.includes(w[i])) {
      const start = i
      while (i + 1 < w.length && VOWELS.includes(w[i + 1])) i++
      let end = i
      // r-controlled：元音组后紧跟 r，r 归入核
      if (end + 1 < w.length && w[end + 1] === 'r') {
        end++
      }
      cores.push([start, end])
    }
    i++
  }
  return cores
}

// magic e 检测：结尾单 e，前核只隔 1 辅音 → e 不算独立核
function detectAndRemoveMagicE(w, cores) {
  if (cores.length < 2) return cores
  const last = cores[cores.length - 1]
  if (w[last[0]] === 'e' && last[0] === last[1] && last[1] === w.length - 1) {
    const prev = cores[cores.length - 2]
    const consBetween = last[0] - prev[1] - 1
    if (consBetween === 1) {
      return cores.slice(0, -1)
    }
  }
  return cores
}

// 主切分函数
function splitSyllables(word) {
  const w = word.toLowerCase().trim()
  if (!w) return []
  if (w.length <= 1) return [w]
  if (!/[aeiouy]/.test(w)) return [w]

  let cores = findVowelCores(w)
  if (cores.length === 0) return [w]

  cores = detectAndRemoveMagicE(w, cores)

  if (cores.length === 1) return [w]

  // 找分割点
  const splits = [0]
  for (let k = 0; k < cores.length - 1; k++) {
    const cur = cores[k]
    const next = cores[k + 1]
    const consStart = cur[1] + 1
    const consEnd = next[0] - 1
    const consCount = consEnd - consStart + 1

    let splitPos
    if (consCount === 0) {
      // VV：直接分开（lion → li/on）
      splitPos = next[0]
    } else if (consCount === 1) {
      // VCV：辅音归后（o-pen）
      splitPos = consStart
    } else if (consCount === 2) {
      // VCCV：digraph 不可拆归后，其余中间分
      const pair = w.slice(consStart, consEnd + 1)
      if (CONSONANT_DIGRAPHS.includes(pair)) {
        splitPos = consStart
      } else {
        splitPos = consStart + 1
      }
    } else {
      // 3+辅音：尾部若是 blend/digraph 保持完整，否则第一个辅音归前
      const tail2 = w.slice(consEnd - 1, consEnd + 1)
      if (CONSONANT_DIGRAPHS.includes(tail2) || CONSONANT_BLENDS.includes(tail2)) {
        splitPos = consEnd - 1
      } else {
        splitPos = consStart + 1
      }
    }
    splits.push(splitPos)
  }
  splits.push(w.length)

  // 切分
  let result = []
  for (let k = 0; k < splits.length - 1; k++) {
    result.push(w.slice(splits[k], splits[k + 1]))
  }

  // -le 修正：若最后音节是单独 'le'，前音节末辅音移过来（table: tab/le → ta/ble）
  // ponytail: 规则覆盖常见词，例外词不维护词库
  if (result.length >= 2 && result[result.length - 1] === 'le') {
    const prev = result[result.length - 2]
    if (prev.length > 1 && /[bcdfghjklmnpqrstvwxz]$/.test(prev)) {
      result[result.length - 2] = prev.slice(0, -1)
      result[result.length - 1] = prev[prev.length - 1] + 'le'
    }
  }

  return result
}

// ============ Grapheme 切分（音节内部）============

function splitGraphemes(syl) {
  if (!syl) return []
  const segments = []

  // -le 结尾特殊处理：le 作为独立段（C+le 音节核心，e 不发音）
  // ponytail: 规则覆盖常见 -le 结尾词，例外不维护词库
  let tail = null
  if (/le$/.test(syl) && syl.length > 2) {
    tail = { text: 'le', type: 'cle', rule: '辅音+le（e不发音）' }
    syl = syl.slice(0, -2)
  }

  let i = 0
  while (i < syl.length) {
    if (VOWELS.includes(syl[i])) {
      // 元音段
      const start = i
      let end = i
      while (end + 1 < syl.length && VOWELS.includes(syl[end + 1])) end++
      let rule = '元音'
      const vowelOnlyText = syl.slice(start, end + 1)
      if (end + 1 < syl.length && syl[end + 1] === 'r') {
        end++
        rule = 'r控制'
      } else if (vowelOnlyText.length > 1) {
        rule = '双元音'
      }
      segments.push({ text: syl.slice(start, end + 1), type: 'vowel', rule })
      i = end + 1
    } else {
      // 辅音段
      const start = i
      let end = i
      while (end + 1 < syl.length && !VOWELS.includes(syl[end + 1])) end++
      const consText = syl.slice(start, end + 1)
      let rule = '辅音'
      if (CONSONANT_DIGRAPHS.includes(consText)) rule = '辅音二合'
      else if (CONSONANT_BLENDS.includes(consText)) rule = '辅音簇'
      else if (DOUBLE_CONSONANTS.includes(consText)) rule = '双辅音'
      segments.push({ text: consText, type: 'consonant', rule })
      i = end + 1
    }
  }

  // 把 -le 尾段加回
  if (tail) segments.push(tail)

  // magic e 标记（相对开音节 a_e/o_e/i_e/u_e/e_e）：辅音正常显示，只标记 a 和 e
  if (!tail && segments.length >= 3) {
    const last = segments[segments.length - 1]
    const prev = segments[segments.length - 2]
    const beforePrev = segments[segments.length - 3]
    if (last.text === 'e' && last.type === 'vowel'
        && prev.type === 'consonant'
        && beforePrev.type === 'vowel' && beforePrev.text.length === 1) {
      const vowelChar = beforePrev.text
      beforePrev.type = 'vce-vowel'
      beforePrev.rule = `相对开音节 ${vowelChar}_e（${vowelChar}发长音）`
      last.type = 'magic-e'
      last.rule = 'magic e（不发音，让元音发长音）'
    }
  }

  return segments
}

// ============ 音节类型判定 ============

function detectSyllableType(syl) {
  if (!syl) return '未知'

  // 1. 辅音+le
  if (/^[bcdfghjklmnpqrstvwxz]+le$/.test(syl)) return '辅音+le音节'

  const segs = splitGraphemes(syl)
  const vowelSegs = segs.filter(s => s.type === 'vowel' || s.type === 'vce-vowel')
  const lastSeg = segs[segs.length - 1]

  // 2. 相对开音节（vce 组）
  if (segs.some(s => s.type === 'vce-vowel')) return '相对开音节'

  // 3. r-控制
  if (vowelSegs.some(s => s.rule === 'r控制')) return 'r控制音节'

  // 4. 辅音+le（结尾段是 cle）
  if (lastSeg && lastSeg.type === 'cle') return '辅音+le音节'

  // 5. 双元音
  if (vowelSegs.some(s => s.rule === '双元音')) return '双元音音节'

  // 5. 开音节：以元音结尾（非 magic e）
  if (lastSeg && lastSeg.type === 'vowel') return '开音节'

  // 6. 闭音节：以辅音结尾
  return '闭音节'
}

// ============ 模块1：音节拆分 ============
const wordInput = ref('')
const syllableResult = ref([])
const exampleWords = ['cat', 'cake', 'football', 'banana', 'apple', 'open', 'water', 'rabbit', 'computer', 'telephone', 'rainbow', 'basketball', 'little', 'candle']

function splitWord() {
  const w = wordInput.value.toLowerCase().trim()
  if (!w) {
    syllableResult.value = []
    return
  }
  const syls = splitSyllables(w)
  const result = syls.map(s => ({
    text: s,
    segments: splitGraphemes(s),
    type: detectSyllableType(s)
  }))

  // 标记跨音节双辅音：前音节末辅音 + 后音节首辅音 相同字母 → 双辅音（发单音）
  for (let i = 0; i < result.length - 1; i++) {
    const curSegs = result[i].segments
    const nextSegs = result[i + 1].segments
    if (curSegs.length === 0 || nextSegs.length === 0) continue
    const lastSeg = curSegs[curSegs.length - 1]
    const firstSeg = nextSegs[0]
    if (lastSeg.type !== 'consonant' || firstSeg.type !== 'consonant') continue
    const lastChar = lastSeg.text[lastSeg.text.length - 1]
    const firstChar = firstSeg.text[0]
    if (lastChar === firstChar && DOUBLE_CONSONANTS.includes(lastChar + firstChar)) {
      lastSeg.rule = '双辅音（发单音）'
      firstSeg.rule = '双辅音（发单音）'
      lastSeg.isDouble = true
      firstSeg.isDouble = true
    }
  }

  syllableResult.value = result
}

// ============ 模块2：音节类型 ============
const typeInput = ref('')
const typeResult = ref(null)

const syllableTypes = [
  { name: '闭音节', pattern: '元音 + 辅音', rule: '元音后面跟着辅音（结尾），元音发短音。', examples: ['cat', 'dog', 'sit', 'bed', 'cup'] },
  { name: '开音节', pattern: '元音结尾', rule: '单词或音节以元音结尾，元音发长音（字母本音）。', examples: ['go', 'me', 'no', 'he', 'she'] },
  { name: '相对开音节', pattern: '元音 + 辅音 + e', rule: '词尾有不发音的 e，前面的元音发长音，e 自己不发音。', examples: ['cake', 'bike', 'home', 'tube', 'kite'] },
  { name: 'R 控制音节', pattern: '元音 + r', rule: '元音后面跟着 r，元音发音受 r 影响，不再发短音或长音。', examples: ['car', 'bird', 'fork', 'turn', 'star'] },
  { name: '双元音音节', pattern: '元音 + 元音', rule: '两个元音字母在一起，通常第一个发长音，第二个不发音。', examples: ['rain', 'boat', 'see', 'train', 'tie'] },
  { name: '辅音 + le 音节', pattern: '辅音 + le', rule: '词尾是辅音 + le，前面的辅音与 le 组成一个无重音音节。', examples: ['apple', 'table', 'little', 'candle', 'bubble'] }
]

function detectType() {
  const w = typeInput.value.toLowerCase().trim()
  if (!w) {
    typeResult.value = null
    return
  }
  const syls = splitSyllables(w)
  typeResult.value = {
    word: w,
    types: syls.map(s => detectSyllableType(s))
  }
}

// ============ 模块3：自然拼读发音参考（按发音分组）============
const pronounceGroups = [
  {
    name: '/æ/ 短 a 音',
    hint: '闭音节中的 a',
    items: [
      { pattern: 'a', word: 'cat' }
    ]
  },
  {
    name: '/eɪ/ 长双元音',
    hint: 'a 的长音',
    items: [
      { pattern: 'a_e', word: 'cake' },
      { pattern: 'ai', word: 'rain' },
      { pattern: 'ay', word: 'play' },
      { pattern: 'ey', word: 'they' }
    ]
  },
  {
    name: '/e/ 短 e 音',
    hint: '闭音节中的 e',
    items: [
      { pattern: 'e', word: 'bed' }
    ]
  },
  {
    name: '/iː/ 长音',
    hint: 'e 的长音',
    items: [
      { pattern: 'e_e', word: 'these' },
      { pattern: 'ee', word: 'see' },
      { pattern: 'ea', word: 'seat' },
      { pattern: 'y', word: 'happy' }
    ]
  },
  {
    name: '/ɪ/ 短 i 音',
    hint: '闭音节中的 i',
    items: [
      { pattern: 'i', word: 'sit' }
    ]
  },
  {
    name: '/aɪ/ 长双元音',
    hint: 'i 的长音',
    items: [
      { pattern: 'i_e', word: 'bike' },
      { pattern: 'igh', word: 'light' },
      { pattern: 'ie', word: 'pie' },
      { pattern: 'y', word: 'fly' }
    ]
  },
  {
    name: '/ɒ/ 短 o 音',
    hint: '闭音节中的 o',
    items: [
      { pattern: 'o', word: 'dog' }
    ]
  },
  {
    name: '/oʊ/ 长双元音',
    hint: 'o 的长音',
    items: [
      { pattern: 'o_e', word: 'home' },
      { pattern: 'oa', word: 'boat' },
      { pattern: 'ow', word: 'low' },
      { pattern: 'o', word: 'go' }
    ]
  },
  {
    name: '/uː/ 长音',
    hint: 'u 的长音',
    items: [
      { pattern: 'u_e', word: 'tube' },
      { pattern: 'ue', word: 'blue' },
      { pattern: 'ew', word: 'chew' },
      { pattern: 'oo', word: 'moon' }
    ]
  },
  {
    name: '/ʌ/ 短 u 音',
    hint: '闭音节中的 u',
    items: [
      { pattern: 'u', word: 'cup' }
    ]
  },
  {
    name: '/ʊ/ 短音',
    hint: '部分 oo 组合',
    items: [
      { pattern: 'oo', word: 'book' }
    ]
  },
  {
    name: '/aʊ/ 双元音',
    hint: 'ou/ow 组合',
    items: [
      { pattern: 'ou', word: 'house' },
      { pattern: 'ow', word: 'cow' }
    ]
  },
  {
    name: '/ɔɪ/ 双元音',
    hint: 'oi/oy 组合',
    items: [
      { pattern: 'oi', word: 'boy' },
      { pattern: 'oy', word: 'toy' }
    ]
  },
  {
    name: 'R 控制元音',
    hint: '元音 + r，发音受 r 影响',
    items: [
      { pattern: 'ar', word: 'car' },
      { pattern: 'er', word: 'her' },
      { pattern: 'ir', word: 'bird' },
      { pattern: 'or', word: 'fork' },
      { pattern: 'ur', word: 'turn' }
    ]
  },
  {
    name: '辅音二合（发单音）',
    hint: '两个辅音字母组合发一个音',
    items: [
      { pattern: 'ch', word: 'chair' },
      { pattern: 'sh', word: 'ship' },
      { pattern: 'th', word: 'think' },
      { pattern: 'ph', word: 'phone' },
      { pattern: 'wh', word: 'white' },
      { pattern: 'ck', word: 'duck' },
      { pattern: 'ng', word: 'sing' },
      { pattern: 'qu', word: 'queen' }
    ]
  },
  {
    name: 'gh 不发音',
    hint: 'gh 组合不发音',
    items: [
      { pattern: 'gh', word: 'high' },
      { pattern: 'igh', word: 'light' },
      { pattern: 'ough', word: 'though' }
    ]
  },
  {
    name: '不发音字母',
    hint: '这些字母组合中有字母不发音',
    items: [
      { pattern: 'kn', word: 'knee' },
      { pattern: 'wr', word: 'write' },
      { pattern: 'mb', word: 'lamb' },
      { pattern: 'gn', word: 'sign' }
    ]
  },
  {
    name: '辅音 + le',
    hint: '词尾辅音 + le，e 不发音',
    items: [
      { pattern: '-ble', word: 'table' },
      { pattern: '-dle', word: 'middle' },
      { pattern: '-ple', word: 'apple' },
      { pattern: '-tle', word: 'little' },
      { pattern: '-kle', word: 'ankle' },
      { pattern: '-fle', word: 'waffle' }
    ]
  }
]

// ============ 模块3搜索 ============
const searchPattern = ref('')
const firstMatchRef = ref(null)

// 过滤分组：分组名匹配则整组显示，否则只显示匹配的 items
const filteredPronounceGroups = computed(() => {
  const q = searchPattern.value.trim().toLowerCase()
  if (!q) return pronounceGroups
  return pronounceGroups
    .map(g => {
      // 分组名或提示匹配，整组显示
      if (g.name.toLowerCase().includes(q) || g.hint.toLowerCase().includes(q)) {
        return g
      }
      // 否则过滤 items：pattern 去下划线包含匹配，或 word 精确匹配
      const items = g.items.filter(it => {
        const pat = it.pattern.toLowerCase().replace(/_/g, '')
        return pat.includes(q) || it.word.toLowerCase() === q
      })
      return { ...g, items }
    })
    .filter(g => g.items.length > 0)
})

// 判断单个 item 是否匹配搜索词（用于高亮）
function isItemMatch(item) {
  const q = searchPattern.value.trim().toLowerCase()
  if (!q) return false
  const pat = item.pattern.toLowerCase().replace(/_/g, '')
  return pat.includes(q) || item.word.toLowerCase() === q
}

// 搜索时滚动到第一个匹配分组
watch(searchPattern, (q) => {
  if (!q.trim()) return
  nextTick(() => {
    if (firstMatchRef.value) {
      firstMatchRef.value.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  })
})

// Web Speech API 朗读
function speak(text, rate = 0.9) {
  if (!('speechSynthesis' in window)) {
    alert('当前浏览器不支持语音朗读')
    return
  }
  window.speechSynthesis.cancel()
  const utter = new SpeechSynthesisUtterance(text)
  utter.lang = 'en-US'
  utter.rate = rate
  window.speechSynthesis.speak(utter)
}
</script>

<style scoped>
.syllable-card {
  padding: 16px 14px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid;
  min-width: 80px;
}
.grapheme-seg {
  display: inline-block;
  padding: 8px 6px;
  margin: 0 1px;
  border-radius: 6px;
  font-size: 24px;
  font-weight: 700;
  min-width: 28px;
  text-align: center;
  cursor: help;
}
.grapheme-seg.vowel {
  background: rgba(251, 191, 36, 0.85);
  color: #0f172a;
  text-decoration: underline;
  text-underline-offset: 4px;
}
.grapheme-seg.consonant {
  background: rgba(148, 163, 184, 0.3);
  color: #e2e8f0;
}
.grapheme-seg.vce-vowel {
  background: rgba(168, 85, 247, 0.7);
  color: #fdf4ff;
  text-decoration: underline;
  text-underline-offset: 4px;
}
.grapheme-seg.magic-e {
  background: rgba(168, 85, 247, 0.5);
  color: #fdf4ff;
  text-decoration: line-through;
  text-decoration-thickness: 1px;
  border: 1px dashed rgba(168, 85, 247, 0.9);
}
.grapheme-seg.cle {
  background: rgba(244, 114, 182, 0.5);
  color: #fdf2f8;
  border: 1px dashed rgba(244, 114, 182, 0.8);
}
.grapheme-seg.cle::after {
  content: '·';
  margin-left: 2px;
  opacity: 0.6;
}
.grapheme-seg.double-consonant {
  background: rgba(34, 211, 238, 0.45);
  color: #ecfeff;
  border: 2px solid rgba(34, 211, 238, 0.9);
  box-shadow: 0 0 8px rgba(34, 211, 238, 0.4);
}
.pronounce-item {
  padding: 12px 8px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  text-align: center;
  transition: all 0.2s;
  cursor: pointer;
}
.pronounce-item:hover {
  background: rgba(251, 191, 36, 0.15);
  border-color: rgba(251, 191, 36, 0.5);
  transform: translateY(-1px);
}
.pronounce-item-highlighted {
  background: rgba(251, 191, 36, 0.25);
  border-color: rgba(251, 191, 36, 0.9);
  box-shadow: 0 0 0 2px rgba(251, 191, 36, 0.4);
}
</style>
