var SaladManager = function() {
    var self = this;

    self.nodes = new vis.DataSet();
    self.edges = new vis.DataSet();

    var container = document.getElementById('network');
    var data = {nodes: self.nodes, edges: self.edges};
    var options = {
        nodes: {
            borderWidthSelected: 2
        },
        physics: {
            maxVelocity: 5
        }
    };
    self.network = new vis.Network(container, data, options);

    self.ingredients = [];
    self.presentSet = new Set();
    self.selectedSet = new Set();
    self.lockedSet = new Set();
    self.connectedSet = new Set();

    self.getFromId = function(id) {
        var match = null;
        self.ingredients.forEach(function(ingredient) {
            if (ingredient.id == id) match = ingredient;
        });
        return match;
    }

    self.getFromName = function(name) {
        var match = null;
        self.ingredients.forEach(function(ingredient) {
            if (ingredient.name == name) match = ingredient;
        });
        return match;
    }

    self.getIngredientNames = function() {
        var names = [];
        self.ingredients.forEach(function(ingredient) {
            names.push(ingredient.name);
        });
        return names;
    }

    self.getNamesFromSet = function(set) {
        var ingredients = Array.from(set);
        var names = [];
        ingredients.forEach(function(ingredient) {
            names.push(ingredient.name);
        });
        return names;
    }

    self.getIngredientsFromNames = function(names) {
        var ingredients = [];
        names.forEach(function(name) {
            ingredients.push(self.getFromName(name));
        });
        return ingredients;
    }
    self.load = function() {
        fetch('/get_salad_ingredients')
        .then(function(response) {
            return response.json();
        }).then(function(ingredients) {
            self.ingredients = []
            ingredients.forEach(function(ingredient) {
                var saladIngredient = new SaladIngredient(self, ingredient);
                self.ingredients.push(saladIngredient);
                self.presentSet.add(saladIngredient);
            });
        }).then(function() {
            self.ingredients.forEach(function(ingredient) {
                ingredient.render();
            });
        }).then(function() {
            $('#present').selectivity({
                items: self.getIngredientNames(),
                multiple: true,
                inputType: 'Multiple',
                placeholder: 'Search ingredients'
            });

            $('#present').on('change', function(event) {
                if (event.added && typeof(event.added) == 'object') {
                    var ingredient = self.getFromName(event.added.id);
                    ingredient.present = true;
                    self.presentSet.add(ingredient);
                    ingredient.render();
                } else if (event.removed && typeof(event.removed) == 'object') {
                    var ingredient = self.getFromName(event.removed.id);
                    ingredient.present = false;
                    self.presentSet.delete(ingredient);
                    ingredient.render();
                }
            });
        });
    };

    self.clickTimeout = null

    self.network.on('click', function(properties) {
        if (self.clickTimeout) {
            clearTimeout(self.clickTimeout);
            self.clickTimeout = null;
        } else {
            self.clickTimeout = setTimeout(function() {
                if (properties.nodes.length > 0) {
                    var ingredient = self.getFromId(properties.nodes[0]);
                    if (ingredient.selected) {
                        if (ingredient.locked) {
                            ingredient.locked = false;
                            self.lockedSet.delete(ingredient);
                        }
                        ingredient.selected = false;
                        self.selectedSet.delete(ingredient);
                    } else {
                        ingredient.selected = true;
                        self.selectedSet.add(ingredient);
                    }
                    ingredient.render();
                }
                self.clickTimeout = null;
            }, 250);
        }
    });

    self.network.on('doubleClick', function(properties) {
        if (properties.nodes.length > 0) {
            var ingredient = self.getFromId(properties.nodes[0]);
            if (!ingredient.selected) {
                ingredient.selected = true;
                self.selectedSet.add(ingredient);
            }
            if (ingredient.locked) {
                ingredient.locked = false;
                self.lockedSet.delete(ingredient)
            } else {
                ingredient.locked = true;
                self.lockedSet.add(ingredient)
            }
            ingredient.render()
        }
    });

    $('#network').contextmenu(function() {
        return false;
    });

    self.network.on('oncontext', function(properties) {
        var id = self.network.getNodeAt({x: properties.pointer.DOM.x, y: properties.pointer.DOM.y});
        if (id != undefined) {
            var ingredient = self.getFromId(id);
            if (ingredient.connected) {
                ingredient.connected = false;
                self.connectedSet.delete(ingredient);
            } else {
                ingredient.connected = true;
                self.connectedSet.add(ingredient);
            }
            ingredient.render();
        }
    });

    self.saveToLocalStorage = function(projectName) {
        if (projectName && projectName != '') {
            var data = {
                presentArray: self.getNamesFromSet(self.presentSet),
                selectedArray: self.getNamesFromSet(self.selectedSet),
                lockedArray: self.getNamesFromSet(self.lockedSet),
                connectedArray: self.getNamesFromSet(self.connectedSet)
            };
            localStorage[projectName] = JSON.stringify(data);

            var projectNamesJson = localStorage.projectNames;
            var projectNamesSet;
            if (projectNamesJson) {
                projectNamesSet = new Set(JSON.parse(projectNamesJson));
            } else {
                projectNamesSet = new Set([]);
            }
            projectNamesSet.add(projectName);
            localStorage.projectNames = JSON.stringify(Array.from(projectNamesSet));
        }

        self.loadFromLocalStorage = function(projectName) {
            if (projectName && projectName != '') {
                var dataJson = localStorage[projectName];
                if (dataJson) {
                    data = JSON.parse(dataJson);
                    self.presentSet = new Set(self.getIngredientsFromNames(data.presentArray));
                    self.selectedSet = new Set(self.getIngredientsFromNames(data.selectedArray));
                    self.lockedSet = new Set(self.getIngredientsFromNames(data.lockedArray));
                    self.connectedSet = new Set(self.getIngredientsFromNames(data.connectedArray));
                    self.ingredients.forEach(function(ingredient) {
                        ingredient.present = self.presentSet.has(ingredient);
                        ingredient.selected = self.selectedSet.has(ingredient);
                        ingredient.locked = self.lockedSet.has(ingredient);
                        ingredient.connected = self.connectedSet.has(ingredient)
                        ingredient.render();
                    });
                } else {
                    console.log('no data found in localStorage')
                }
            }
        }
    }

    $('#save').click(function() {
        var message = '';
        var projectNamesJson = localStorage.projectNames;
        if (projectNamesJson) {
            message += 'Saved projects:\n';
            JSON.parse(projectNamesJson).forEach(function(name) {
                message += name + '\n';
            });
        } else {
            message += 'No saved projects.\n';
        }
        message += '\nPlease enter a name to save under:';
        var projectName = prompt(message);

        if (projectName && projectName != '') {
            self.saveToLocalStorage(projectName);
            console.log('SAVED');
        }
    });

    $('#load').click(function() {
        var projectNamesJson = localStorage.projectNames;
        var projectNames;
        if (projectNamesJson) {
            projectNames = JSON.parse(projectNamesJson);
        } else {
            projectNames = [];
        }

        var message = '';
        var projectNamesJson = localStorage.projectNames;
        if (projectNamesJson) {
            message += 'Saved projects:\n';
            JSON.parse(projectNamesJson).forEach(function(name) {
                message += name + '\n';
            });
        } else {
            message += 'No saved projects.\n';
        }
        message += '\nPlease enter a project to load:';
        var projectName = prompt(message);

        if (projectName && projectName != '') {
            var projectNameSet = new Set(projectNames);
            if (!projectNameSet.has(projectName)) {
                alert('Project not found, please try again.')
            } else {
                self.loadFromLocalStorage(projectName);
                console.log('LOADED');
            }
        }
    });

    $('#generate').click(function() {

    });
}
