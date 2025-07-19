import { defineStore } from 'pinia';
import { ref } from 'vue';
import { processingService } from '../services/api';
import { useNotificationStore } from './notificationStore';
import { useReportsStore } from './reportsStore';

export const useJobStatusStore = defineStore('jobStatus', () => {
    // State
    const activeJobId = ref(null);
    const jobStatus = ref('');
    const jobMessage = ref('');
    let pollInterval = null;

    // Actions
    function clearJobState() {
        activeJobId.value = null;
        jobStatus.value = '';
        jobMessage.value = '';
        if (pollInterval) {
            clearInterval(pollInterval);
            pollInterval = null;
        }
    }

    async function startProcessingJob(jobDetails) {
        const notificationStore = useNotificationStore();
        clearJobState(); // Clear any previous job

        try {
            const response = await processingService.startProcessingJob(jobDetails);
            activeJobId.value = response.jobId;
            jobStatus.value = 'pending';
            jobMessage.value = 'Job submitted... waiting for status updates.';
            startPolling(response.jobId);
        } catch (error) {
            // Handled by api service
        }
    }

    function startPolling(jobId) {
        const notificationStore = useNotificationStore();
        const reportsStore = useReportsStore();

        pollInterval = setInterval(async () => {
            try {
                const update = await processingService.getJobStatus(jobId);
                jobStatus.value = update.status;
                jobMessage.value = update.message;

                if (update.status === 'complete' || update.status === 'failed') {
                    clearInterval(pollInterval);
                    if (update.status === 'complete') {
                        notificationStore.addNotification({ message: 'Report generated successfully!', type: 'success' });
                        // Refresh the reports list to show the new report
                        await reportsStore.fetchReports();
                    } else {
                        notificationStore.addNotification({ message: 'Report generation failed.', type: 'error' });
                    }
                    // Keep the final status message for a few seconds before clearing
                    setTimeout(clearJobState, 5000);
                }
            } catch (error) {
                clearInterval(pollInterval);
                clearJobState();
            }
        }, 2000); // Poll every 2 seconds
    }

    return {
        activeJobId,
        jobStatus,
        jobMessage,
        startProcessingJob,
    };
});
