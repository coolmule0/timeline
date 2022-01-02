import EntryFilter from './filter.js'
import EntryMap from './previews/geolocation.js'
import JournalEntry from './entries/journal.js'
import JournalNewEntry from './entries/journalNew.js'
import Preview from './preview.js';
import SpinnerComponent from './spinner.js';
import TimelineActivityEntry from './entries/activity.js';
import TimelineImageEntry from './entries/image.js';
import TimelineJournalEntry from './entries/journal.js'
import TimelineMessageEntry from './entries/message.js';
import TimelineMotionEntry from './entries/motion.js';
import TimelineNav from './timeline-nav.js';
import TimelinePostEntry from './entries/post.js'
import TimelineTextEntry from './entries/text.js';
import TimelineVideoEntry from './entries/video.js';
import TransactionEntry from './entries/transaction.js';
import { filters } from './../models/filters.js';
import { RequestStatus } from './../models/requests.js';

function makeRouteValid(to, from, next) {
  // Enforce a valid current date in the route
  if (to.query.date) {
    const newDate = moment(to.query.date, 'YYYY-MM-DD', true);
    if(newDate.isValid()) {
      next();
      return;
    }
  }
  next({
    name: 'timeline', query: { date: moment().format('YYYY-MM-DD') }
  });
}

export default Vue.component('timeline', {
  data: function() {
    return {
      selectedEntry: null,
      filters: filters,
    }
  },
  created: function() {
    this.$store.dispatch('timeline/getEntries');
  },
  watch: {
    '$route.query.date': function() {
      this.$store.dispatch('timeline/getEntries', true)
    }
  },
  beforeRouteEnter: makeRouteValid,
  beforeRouteUpdate: makeRouteValid,
  computed: {
    timelineDate: function(){
      return moment(this.$store.state.route.query.date, 'YYYY-MM-DD', true);
    },
    relativeTimelineDate: function() {
      const duration = this.timelineDate.diff(moment().startOf('day'));
      return duration !== 0 ? moment.duration(duration).humanize(true) : 'today';
    },
    entries: function() {
      return this.$store.getters['timeline/filteredEntries'];
    },
    isLoading: function() {
      return this.$store.state.timeline.entriesRequestStatus === RequestStatus.PENDING;
    },
    transactionsEntries: function() {
      return this.entries.filter(this.filters.transaction.filterFunction);
    },
  },
  methods: {
    openPreview: function(entry) {
      this.selectedEntry = entry;
    },
    closePreview: function() {
      this.selectedEntry = null;
    },
    entryType: function(entry) {
      const s = entry.schema;
      if(s.startsWith('activity.browsing')) {
        return 'activity-entry';
      }
      else if (s.startsWith('file.image') || s.startsWith('file.document.pdf')) {
        return 'image-entry';
      }
      else if(s === 'journal') {
        return 'journal-entry';
      }
      else if(s.startsWith('message.')) {
        return 'message-entry';
      }
      else if(s.startsWith('activity.exercise.session')) {
        return 'motion-entry';
      }
      else if(s.startsWith('social.')) {
        return 'post-entry';
      }
      else if(s.startsWith('file.text')) {
        return 'text-entry';
      }
      else if(s.startsWith('file.video')) {
        return 'video-entry';
      }
    },
  },
  template: `
    <div id="timeline">
      <header>
        <timeline-nav id="timeline-nav"></timeline-nav>
        <router-link :to="{ name: 'settings'}" class="button"><i class="fas fa-cogs"></i></router-link>
      </header>
      <main class="content-with-sidebar">
        <div class="sidebar">
          <h1 class="current-date">{{ timelineDate.format('LL') }}</h1>
          <span class="subtitle">{{ timelineDate.format('dddd') }}, {{ relativeTimelineDate }}</span>
          <entry-map class="map" v-show="!isLoading" :entries="entries"></entry-map>
          <ul class="recap" v-if="!isLoading">
            <li v-for="(filter, filterName) in filters"><entry-filter :name="filterName"></entry-filter></li>
          </ul>
        </div>
        <spinner v-if="isLoading"></spinner>
        <div class="content entries">
          <new-journal-entry v-if="!isLoading"></new-journal-entry>
          <component
            :entry="entry"
            :is="entryType(entry)"
            :key="entry.id"
            @select="openPreview"
            class="entry"
            v-for="entry in entries"
            v-if="entryType(entry) && !isLoading"></component>
          <div class="separator" v-if="transactionsEntries.length">Unknown time</div>
          <transaction-entry
            :entry="entry"
            class="entry"
            v-for="entry in transactionsEntries"></transaction-entry>
        </div>
      </main>
      <preview :entry="selectedEntry" v-if="selectedEntry" @close="closePreview"></preview>
    </div>
  `
});