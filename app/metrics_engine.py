import os
import importlib
import inspect
import numpy as np

from metric import Metric


class MetricsEngine:
    def __init__(self):
        self.metrics_list = []
        self.view = None
        pass

    def load_metrics(self, path: str = "") -> None:
        if path == "":
            path = os.path.join(os.path.dirname(os.getcwd()), "plugins")
        try:
            plugins_list = os.listdir(path)
        except:
            try:
                path = path[1:]
                plugins_list = os.listdir(path)
            except:
                try:
                    path = path[2:]
                    plugins_list = os.listdir(path)
                except:
                    raise Exception("No plugins folder found!")

        plugins = []
        for plugin in plugins_list:
            if '_metric.py' in plugin:
                if not os.path.isdir(plugin):
                    plugins.append(plugin)

        if not len(plugins) > 0:
            raise Exception("No plugin in plugins folder found!")

        for plugin in plugins:
            module_str = f"{path.replace('/', '')}"
            module_str = f"{module_str.replace('.', '')}"
            spec = importlib.util.spec_from_file_location(module_str, f"{path}/{plugin}")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            functions = inspect.getmembers(module, inspect.isfunction)

            for func in functions:
                name, function = func
                if '_metric' in name:
                    break

            self.metrics_list.append(Metric(name, function))

    def calculate_metrics(self, reference_image: np.asarray, modified_image: np.asarray) -> None:
        if self.view is not None:
            results = []
            for metric in self.metrics_list:
                results.append({'name': metric.name, 'value': float(metric.compute(reference_image, modified_image))})
            self.view.display_metrics(results)
        else:
            raise Exception("calculate_metrics", "view is not set")

    def subscribe_view(self, view) -> None:
        self.view = view
