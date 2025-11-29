import { defineComponent, ref } from 'vue'

export default defineComponent({
  name: 'DrawCarousel',
  props: {
    draws: {
      type: Array,
      default: () => []
    }
  },
  setup(props) {
    const index = ref(0)

    const next = () => {
      index.value = (index.value + 1) % Math.max(props.draws.length || 1, 1)
    }

    const current = () => props.draws[index.value] || { numbers: [], stars: [] }

    return () => (
      <div class="card">
        <h3>Carousel des tirages</h3>
        <p>Nombres: {current().numbers.join(', ')}</p>
        <p>Étoiles: {current().stars.join(', ')}</p>
        <button class="button-primary" onClick={next}>Suivant</button>
      </div>
    )
  }
})
