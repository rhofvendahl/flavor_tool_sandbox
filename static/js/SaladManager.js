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

    self.existsInLocalStorage = function(varName) {
        var varJson = localStorage['salad_' + varName];
        if (varJson) {
            return true;
        } else {
            return false;
        }
    }

    self.getFromLocalStorage = function(varName) {
        var varJson = localStorage['salad_' + varName];
        if (varJson) { // since I want this to execute if varJson is truthy
            return JSON.parse(varJson);
        } else {
            return null;
        }
    }

    self.saveToLocalStorage = function(varName, varContent) {
        localStorage['salad_' + varName] = JSON.stringify(varContent);
    }

    self.saveProjectToLocalStorage = function(projectName) {
        if (projectName != undefined) {
            console.log('SAVING TO LOCAL STORAGE');
            var data = {
                presentArray: self.getNamesFromSet(self.presentSet),
                selectedArray: self.getNamesFromSet(self.selectedSet),
                lockedArray: self.getNamesFromSet(self.lockedSet),
                connectedArray: self.getNamesFromSet(self.connectedSet)
            };
            // console.log('PRESENT', data.presentArray);
            // console.log('SELECTED', data.selectedArray);
            // console.log('LOCKED', data.lockedArray);
            // localStorage['salad_'projectName] = JSON.stringify(data);
            self.saveToLocalStorage(projectName, data);

            // var projectNamesJson = localStorage.projectNames;
            var projectNamesSet;
            if (self.existsInLocalStorage('projectNames')) {
                projectNamesSet = new Set(self.getFromLocalStorage('projectNames'));
            } else {
                projectNamesSet = new Set([]);
            }
            projectNamesSet.add(projectName);
            console.log(projectNamesSet)
            self.saveToLocalStorage('projectNames', Array.from(projectNamesSet));
            // localStorage.projectNames = JSON.stringify(Array.from(projectNamesSet));
        }
    }

    self.loadProjectFromLocalStorage = function(projectName) {
        if (projectName != undefined) {
            console.log('LOADING FROM LOCAL STORAGE');
            // var dataJson = localStorage[projectName];
            if (self.existsInLocalStorage(projectName)) {
                data = self.getFromLocalStorage(projectName);
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

    self.load = function() {
        // var aboutedJson = localStorage.salad_abouted;
        if (!self.existsInLocalStorage('abouted') || self.getFromLocalStorage('abouted') == false) {
            // console.log('backing shit the fuck up.')
            // self.saveToLocalStorage('current', JSON.parse(localStorage.current))
            self.saveToLocalStorage('projectNames', new Set(['salad_current']))
            // var projectNamesSet;
            // if (self.existsInLocalStorage('projectNames')) {
            //     projectNamesSet = new Set(self.getFromLocalStorage('projectNames'));
            // } else {
            //     projectNamesSet = new Set([]);
            // }
            // projectNamesSet.add(projectName);
            // console.log(projectNamesSet)
            // self.saveToLocalStorage('projectNames', Array.from(projectNamesSet));

            console.log('Showing "About" to first time visitors!');
            $('#about-window').show();
            self.saveToLocalStorage('abouted', true);
            // localStorage.salad_abouted = JSON.stringify(true);
        }
        fetch('/get_salad_ingredients', {
            method: 'get'
        }).then(function(response) {
            return response.json();
        }).then(function(ingredients) {
            self.ingredients = []
            ingredients.forEach(function(ingredient) {
                var saladIngredient = new SaladIngredient(self, ingredient);
                self.ingredients.push(saladIngredient);
                self.presentSet.add(saladIngredient);
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
                    ingredient.clear();
                    ingredient.render();
                }
            });
        }).then(function() { // idk if this is set up right, the way render is an alternative to load
            if (self.existsInLocalStorage('')) {
                console.log('CACHE FOUND');
                self.loadProjectFromLocalStorage('');
            } else {
                self.ingredients.forEach(function(ingredient) {
                    ingredient.render();
                });
            }
        });
    };

    self.clickTimeout = null;

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
                    self.saveProjectToLocalStorage('');
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
            self.saveProjectToLocalStorage('');
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
            self.saveProjectToLocalStorage('');
        }
    });

    $('#save').click(function() {
        var message = '';
        if (self.existsInLocalStorage('projectNames')) {
            message += 'Saved projects:\n';
            self.getFromLocalStorage('projectNames').forEach(function(name) {
                if (name != '') {
                    message += name + '\n';
                }
            });
        } else {
            message += 'No saved projects.\n';
        }
        message += '\nPlease enter a name to save under:';
        var projectName = prompt(message);

        if (projectName && projectName != '') {
            self.saveProjectToLocalStorage(projectName);
            console.log('SAVED');
        }
    });

    $('#load').click(function() {
        console.log(localStorage);
        // var projectNamesExists = self.existsInLocalStorage('projectNames');
        // var projectNames;
        var message = '';
        var projectNames;
        if (self.existsInLocalStorage('projectNames')) {
            projectNames = self.getFromLocalStorage('projectNames');
            message += 'Saved projects:\n';
            self.getFromLocalStorage('projectNames').forEach(function(name) {
                if (name != '') {
                    message += name + '\n';
                }
            });
        } else {
            message += 'No saved projects.\n';
            var projectNames = [];
        }

        message += '\nPlease enter a project to load:';
        var projectName = prompt(message);

        if (projectName && projectName != '') {
            var projectNameSet = new Set(projectNames);
            if (!projectNameSet.has(projectName)) {
                alert('Project not found, please try again.')
            } else {
                self.loadProjectFromLocalStorage(projectName);
                console.log('LOADED');
                self.saveProjectToLocalStorage('');
            }
        }
    });

    $('#generate').click(function() {

    });

    // $('#about-window').hide();
    $('#about').click(function() {
        $('#about-window').show();
    });
    $('#about-close').click(function() {
        $('#about-window').hide();
    });

    $('#all').click(function() {
        var confirmation = prompt('Are you sure? (y/n)');
        if (confirmation == 'y') {
            self.ingredients.forEach(function(ingredient) {
                ingredient.present = true;
                ingredient.render();
            });
            self.saveProjectToLocalStorage('');
        }
    });

    $('#none').click(function() {
        var confirmation = prompt('Are you sure? (y/n)');
        if (confirmation == 'y') {
            self.ingredients.forEach(function(ingredient) {
                ingredient.clear();
                ingredient.render();
            });
            self.saveProjectToLocalStorage('');
        }
    });

    self.generate = function() {
        $('#generating').show();
        fetch('/generate_salad', {
            method: 'post',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                present: self.getNamesFromSet(self.presentSet),
                locked: self.getNamesFromSet(self.lockedSet)
            })
        }).then(function(response) {
            // console.log('dealing with fetch response')
            // console.log(response);
            return response.json();
        }).then(function(json) {
            var presentNames = json['present_names'];
            var selectedNames = json['selected_names'];
            var lockedNames = json['locked_names'];
            var generatedNames = json['generated_names'];

            var presentNamesSet = new Set(presentNames);
            var selectedNamesSet = new Set(selectedNames);
            var lockedNamesSet = new Set(lockedNames);
            var generatedNamesset = new Set(generatedNames);

            self.ingredients.forEach(function(ingredient) {
                if (presentNamesSet.has(ingredient.name) && !ingredient.present) {
                    ingredient.present = true;
                    self.presentSet.add(ingredient);
                } // no else clause, as I don't want to remove any ingredients added since the request was sent
                ingredient.selected = selectedNamesSet.has(ingredient.name);
                ingredient.locked = lockedNamesSet.has(ingredient.name);
                // console.log('name', ingredient.name);
                // console.log('present', ingredient.present);
                // console.log('selected', ingredient.selected);
                // console.log('locked', ingredient.locked);
                // console.log('');
                $('#generating').hide();
            });
            self.selectedSet = new Set(self.getIngredientsFromNames(selectedNames));
            self.lockedSet = new Set(self.getIngredientsFromNames(lockedNames));

            self.ingredients.forEach(function(ingredient) {
                ingredient.render();
            });

            self.saveProjectToLocalStorage('');
        });
    }

    $('#generate').click(function() {
        self.generate();
    });

    $('body').keydown(function(event){
        // if (event.keyCode == 32 && document.activeElement.tagName != 'INPUT') {
        if (event.keyCode == 32) {
            $(document.activeElement).blur();
            self.generate();
        }
    });
}
