<template>
  <div class="p-4 h-full flex flex-col bg-gray-50">
    <h3 class="text-base font-semibold text-gray-700 mb-3">Document Relationship Graph</h3>
    <div ref="networkContainer" class="flex-1 w-full h-full border rounded-md bg-white shadow"></div>
     <div v-if="!documents || documents.length === 0" class="text-center text-gray-500 py-10">
      <Spline class="h-10 w-10 mx-auto text-gray-400 mb-2"/> <p class="text-sm">No documents with relationship data to display in the graph.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onBeforeUnmount, defineProps, defineEmits } from 'vue';
import { Network } from 'vis-network/standalone';
import 'vis-network/styles/vis-network.min.css';
import { Spline } from 'lucide-vue-next'; // Changed icon import

const props = defineProps({
  documents: {
    type: Array,
    required: true,
    default: () => []
  },
  highlightedDocumentIds: {
    type: Array,
    default: () => []
  }
});
const emit = defineEmits(['document-click']);

const networkContainer = ref(null);
let networkInstance = null;

const formatDataForNetwork = (docs) => {
  const nodes = docs.map(doc => ({
    id: doc.id,
    label: doc.name.length > 20 ? doc.name.substring(0, 17) + '...' : doc.name,
    title: `${doc.name}\nStream: ${doc.streamName}\nSubjects: ${(doc.subjects || []).join(', ')}`,
    group: doc.streamId,
    shape: 'box',
    color: props.highlightedDocumentIds.includes(doc.id) ? { border: '#facc15', background: '#fef9c3', highlight: { border: '#fde047', background: '#fefce8'} } : undefined,
    font: {
        color: props.highlightedDocumentIds.includes(doc.id) ? '#713f12' : '#333333',
        size: 12,
    },
    margin: 10,
    widthConstraint: { maximum: 150 }
  }));

  const edges = [];
  docs.forEach(doc => {
    if (doc.parentId) {
      if (nodes.find(n => n.id === doc.parentId)) { // Check if parent node exists
        edges.push({ from: doc.parentId, to: doc.id, arrows: 'to', dashes: true, color: { color: '#a1a1aa', highlight: '#71717a'} });
      }
    }
    if (doc.linkedDocIds && doc.linkedDocIds.length > 0) {
      doc.linkedDocIds.forEach(linkedId => {
        if (nodes.find(n => n.id === linkedId)) { // Check if linked node exists
            edges.push({ from: doc.id, to: linkedId, arrows: 'to;from', color: { color: '#a1a1aa', highlight: '#71717a'} });
        }
      });
    }
  });
  return { nodes, edges };
};


onMounted(() => {
  if (networkContainer.value && props.documents.length > 0) {
    const data = formatDataForNetwork(props.documents);
    if (data.nodes.length === 0) return;

    const options = {
      layout: {
        hierarchical: false,
      },
      nodes: {
        borderWidth: 1,
        borderWidthSelected: 2,
        shapeProperties: {
            borderRadius: 3
        }
      },
      edges: {
        smooth: {
            type: 'cubicBezier',
            forceDirection: 'horizontal',
            roundness: 0.4
        },
        width: 1,
      },
      physics: {
        enabled: true,
        solver: 'barnesHut',
        barnesHut: {
          gravitationalConstant: -2000,
          centralGravity: 0.1,
          springLength: 150,
          springConstant: 0.02,
          damping: 0.09,
          avoidOverlap: 0.3
        },
        minVelocity: 0.75
      },
      interaction: {
        hover: true,
        tooltipDelay: 200,
        dragNodes: true,
        dragView: true,
        zoomView: true
      },
    };
    networkInstance = new Network(networkContainer.value, data, options);

    networkInstance.on('selectNode', (params) => {
      if (params.nodes.length > 0) {
        const selectedDocId = params.nodes[0];
        const doc = props.documents.find(d => d.id === selectedDocId);
        if (doc) {
          emit('document-click', doc);
        }
      }
    });
  }
});

watch(() => [props.documents, props.highlightedDocumentIds], () => {
  if (networkInstance) {
    const data = formatDataForNetwork(props.documents);
    if (data.nodes.length > 0) {
        networkInstance.setData(data);
    } else {
        networkInstance.setData({nodes: [], edges: []});
    }
  } else if (networkContainer.value && props.documents.length > 0) {
    const data = formatDataForNetwork(props.documents);
    if (data.nodes.length === 0) return;
    const options = { /* options from onMounted */
        layout: { hierarchical: false },
        nodes: { borderWidth: 1, borderWidthSelected: 2, shapeProperties: { borderRadius: 3 }},
        edges: { smooth: { type: 'cubicBezier', forceDirection: 'horizontal', roundness: 0.4 }, width: 1},
        physics: { enabled: true, solver: 'barnesHut', barnesHut: { gravitationalConstant: -2000, centralGravity: 0.1, springLength: 150, springConstant: 0.02, damping: 0.09, avoidOverlap: 0.3}, minVelocity: 0.75 },
        interaction: { hover: true, tooltipDelay: 200, dragNodes: true, dragView: true, zoomView: true },
    };
    networkInstance = new Network(networkContainer.value, data, options);
    networkInstance.on('selectNode', (params) => {
      if (params.nodes.length > 0) {
        const selectedDocId = params.nodes[0];
        const doc = props.documents.find(d => d.id === selectedDocId);
        if (doc) {
          emit('document-click', doc);
        }
      }
    });
  }
}, { deep: true });

onBeforeUnmount(() => {
  if (networkInstance) {
    networkInstance.destroy();
    networkInstance = null;
  }
});

</script>

<style>
.vis-network {
  border: 1px solid #e5e7eb; /* gray-200 */
  border-radius: 0.375rem; /* rounded-md */
}
div.vis-tooltip {
  font-family: 'Inter', sans-serif;
  font-size: 12px;
  padding: 8px;
  background-color: #333;
  color: white;
  border: none;
  border-radius: 4px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
  max-width: 300px;
  white-space: pre-wrap;
}
</style>
