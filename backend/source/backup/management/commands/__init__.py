import logging
from itertools import chain

from django.core.management import BaseCommand

from backup.utils.models import get_models_by_name

logger = logging.getLogger(__name__)


class ModelProcessingCommand(BaseCommand):
    class_name = 'models'
    default_class = None

    def handle(self, *args, **options):
        classes_to_process = get_models_by_name(options.get('classes_to_process') or [self.default_class.__name__])
        logger.info(f"Processing {self.class_name} types: {[model.__name__ for model in classes_to_process]}")

        instances_to_process = list(chain.from_iterable([c.objects.all() for c in classes_to_process]))

        preprocessing_tasks = set()
        postprocessing_tasks = set()

        for instance in instances_to_process:
            preprocessing_tasks.update(instance.get_preprocessing_tasks())
            postprocessing_tasks.update(instance.get_postprocessing_tasks())

        logger.info(f"Running {len(preprocessing_tasks)} preprocessing tasks")
        for task in preprocessing_tasks:
            task()

        failure_count = 0
        for instance in instances_to_process:
            try:
                logger.info(f"Processing {self.class_name} {instance}")
                created_entries, updated_entries = instance.process(force=options['force'])
                logger.info(
                    f"Retrieved {created_entries + updated_entries} entries for {self.class_name} {instance}. "
                    f"{created_entries} created, {updated_entries} updated."
                )
            except:
                logger.exception(f"Failed to process {self.class_name} {str(instance)}")
                failure_count += 1

        logger.info(f"{len(instances_to_process)} {self.class_name} instances processed. "
                    f"{len(instances_to_process) - failure_count} successful, {failure_count} failed.")

        logger.info(f"Running {len(postprocessing_tasks)} postprocessing tasks")
        for task in postprocessing_tasks:
            task()

        logger.info(f"All {self.class_name} types processed")

    def add_arguments(self, parser):
        parser.add_argument(
            'classes_to_process',
            nargs='*',
            type=str,
            help=f'One or more {self.class_name} class names to process. By default, all {self.class_name} types are '
                 'processed.',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help=f'Reprocess {self.class_name} that do not need to be processed.',
        )
