<template>
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <div class="lg:col-span-2">
      <div class="canvas-container p-4">
        <div ref="containerRef" class="w-full h-[500px]"></div>
      </div>
    </div>
    
    <div class="control-panel p-4">
      <h3 class="text-lg font-semibold text-gray-800 mb-4">3D图形</h3>
      
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">选择图形</label>
          <select v-model="selectedShape" @change="changeShape" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent">
            <option v-for="shape in shapes" :key="shape.id" :value="shape.id">{{ shape.name }}</option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">旋转速度: {{ rotationSpeed }}</label>
          <input type="range" v-model.number="rotationSpeed" min="0" max="10" step="0.5" class="w-full">
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">图形大小: {{ scale }}</label>
          <input type="range" v-model.number="scale" min="0.5" max="2" step="0.1" @input="updateScale" class="w-full">
        </div>
        
        <div>
          <label class="flex items-center space-x-2">
            <input type="checkbox" v-model="autoRotate" class="w-4 h-4 text-purple-600 rounded">
            <span class="text-sm text-gray-700">自动旋转</span>
          </label>
        </div>
        
        <div class="pt-4 border-t border-gray-200">
          <button @click="resetView" class="w-full py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors">
            重置视角
          </button>
        </div>
        
        <div class="pt-4">
          <h4 class="text-sm font-medium text-gray-700 mb-2">图形属性</h4>
          <div class="text-xs text-gray-600 space-y-1">
            <div>体积: {{ volume.toFixed(2) }}</div>
            <div>表面积: {{ surfaceArea.toFixed(2) }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import * as THREE from 'three'

const containerRef = ref(null)
const selectedShape = ref('sphere')
const rotationSpeed = ref(2)
const scale = ref(1)
const autoRotate = ref(true)

const shapes = [
  { id: 'sphere', name: '球体', volume: r => (4/3) * Math.PI * Math.pow(r, 3), surfaceArea: r => 4 * Math.PI * Math.pow(r, 2) },
  { id: 'cube', name: '正方体', volume: r => Math.pow(r * 2, 3), surfaceArea: r => 6 * Math.pow(r * 2, 2) },
  { id: 'cone', name: '圆锥体', volume: r => (1/3) * Math.PI * Math.pow(r, 2) * (r * 2), surfaceArea: r => Math.PI * r * (r + Math.sqrt(Math.pow(r, 2) + Math.pow(r * 2, 2))) },
  { id: 'cylinder', name: '圆柱体', volume: r => Math.PI * Math.pow(r, 2) * (r * 2), surfaceArea: r => 2 * Math.PI * r * (r + r * 2) },
  { id: 'torus', name: '圆环', volume: () => 0, surfaceArea: () => 0 },
  { id: 'octahedron', name: '八面体', volume: r => (4/3) * Math.pow(r, 3), surfaceArea: r => 2 * Math.sqrt(3) * Math.pow(r, 2) }
]

let scene, camera, renderer, mesh, animationId

const volume = computed(() => {
  const shape = shapes.find(s => s.id === selectedShape.value)
  return shape ? shape.volume(1) * Math.pow(scale.value, 3) : 0
})

const surfaceArea = computed(() => {
  const shape = shapes.find(s => s.id === selectedShape.value)
  return shape ? shape.surfaceArea(1) * Math.pow(scale.value, 2) : 0
})

const initScene = () => {
  if (!containerRef.value) return
  
  scene = new THREE.Scene()
  scene.background = new THREE.Color(0xf5f5f5)
  
  const width = containerRef.value.clientWidth
  const height = 500
  
  camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000)
  camera.position.z = 5
  
  renderer = new THREE.WebGLRenderer({ antialias: true })
  renderer.setSize(width, height)
  renderer.setPixelRatio(window.devicePixelRatio)
  containerRef.value.appendChild(renderer.domElement)
  
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.6)
  scene.add(ambientLight)
  
  const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8)
  directionalLight.position.set(5, 5, 5)
  scene.add(directionalLight)
  
  createShape()
  animate()
}

const createShape = () => {
  if (mesh) {
    scene.remove(mesh)
  }
  
  let geometry
  
  switch(selectedShape.value) {
    case 'sphere':
      geometry = new THREE.SphereGeometry(1, 32, 32)
      break
    case 'cube':
      geometry = new THREE.BoxGeometry(2, 2, 2)
      break
    case 'cone':
      geometry = new THREE.ConeGeometry(1, 2, 32)
      break
    case 'cylinder':
      geometry = new THREE.CylinderGeometry(1, 1, 2, 32)
      break
    case 'torus':
      geometry = new THREE.TorusGeometry(1, 0.3, 16, 100)
      break
    case 'octahedron':
      geometry = new THREE.OctahedronGeometry(1)
      break
    default:
      geometry = new THREE.SphereGeometry(1, 32, 32)
  }
  
  const material = new THREE.MeshPhongMaterial({
    color: 0x8b5cf6,
    shininess: 100,
    transparent: true,
    opacity: 0.8
  })
  
  mesh = new THREE.Mesh(geometry, material)
  mesh.scale.set(scale.value, scale.value, scale.value)
  scene.add(mesh)
}

const animate = () => {
  animationId = requestAnimationFrame(animate)
  
  if (mesh && autoRotate.value) {
    mesh.rotation.x += 0.01 * rotationSpeed.value
    mesh.rotation.y += 0.01 * rotationSpeed.value
  }
  
  renderer.render(scene, camera)
}

const changeShape = () => {
  createShape()
}

const updateScale = () => {
  if (mesh) {
    mesh.scale.set(scale.value, scale.value, scale.value)
  }
}

const resetView = () => {
  if (mesh) {
    mesh.rotation.x = 0
    mesh.rotation.y = 0
  }
  camera.position.z = 5
}

const handleResize = () => {
  if (!containerRef.value || !camera || !renderer) return
  
  const width = containerRef.value.clientWidth
  const height = 500
  
  camera.aspect = width / height
  camera.updateProjectionMatrix()
  renderer.setSize(width, height)
}

onMounted(() => {
  initScene()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (animationId) {
    cancelAnimationFrame(animationId)
  }
  if (renderer) {
    renderer.dispose()
  }
})

watch([selectedShape, scale], () => {
  createShape()
})
</script>
