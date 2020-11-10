export default Vue.component('preview', {
  props: ['entry'],
  computed: {
    mimetype: function(){
      if (this.entry.extra_attributes) {
        return this.entry.extra_attributes.mimetype;
      }
      return undefined;
    },
    previewType: function() {
      if(this.entry.schema.startsWith('file.video')) {
        return 'video';
      }
      else if(this.entry.schema.startsWith('file.image') || this.entry.schema.startsWith('file.document.pdf')) {
        return 'image';
      }
      else if(this.entry.schema.startsWith('social.')) {
        return 'image';
      }
    },
    imageSrcSet: function() {
        return `${this.entry.extra_attributes.previews.preview} 1x, ${this.entry.extra_attributes.previews.preview2x} 2x`;
    }
  },
  methods: {
    close: function(event) {
      this.$emit('close');
    }
  },
  template: `
    <div class="preview">
      <button class="button close" @click="close" title="Close"><i class="fas fa-times"></i></button>
      <img
        v-if="previewType === 'image'"
        :alt="entry.title"
        :src="entry.extra_attributes.previews.preview"
        :srcset="imageSrcSet"
        />
      <video autoplay controls v-if="previewType === 'video'" :alt="entry.title" :src="entry.extra_attributes.previews.preview"/>
      <post :entry="entry" v-if="previewType === 'post'"></post>
    </div>
  `
});