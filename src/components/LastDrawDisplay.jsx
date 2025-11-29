import { defineComponent } from 'vue'

export default defineComponent({
  name: 'LastDrawDisplay',
  props: {
    draw: {
      type: Object,
      default: () => ({ numbers: [], stars: [] })
    }
  },
  setup(props) {
    return () => (
      <div class="card">
        <h3>Dernier tirage</h3>
        <p>Nombres: {props.draw.numbers?.join(', ') || '—'}</p>
        <p>Étoiles: {props.draw.stars?.join(', ') || '—'}</p>
      </div>
    )
  }
})
