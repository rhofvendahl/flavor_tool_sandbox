var StirFryManager = function() {
    var self = this;

    self.nodes = new vis.DataSet();
    self.edges = new vis.DataSet();
    var container = document.getElementById('network');
    var data = {nodes: self.nodes, edges: self.edges};
    var options = {
        height: window.innerHeight + 'px',
        nodes: {
            borderWidthSelected: 2,
            font: {
                size: 12
            }
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
        var varJson = localStorage['stir_fry_' + varName];
        if (varJson) {
            return true;
        } else {
            return false;
        }
    }

    self.getFromLocalStorage = function(varName) {
        var varJson = localStorage['stir_fry_' + varName];
        if (varJson) { // since I want this to execute if varJson is truthy
            return JSON.parse(varJson);
        } else {
            return null;
        }
    }

    self.saveToLocalStorage = function(varName, varContent) {
        localStorage['stir_fry_' + varName] = JSON.stringify(varContent);
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
            self.saveToLocalStorage(projectName, data);

            var projectNamesSet;
            if (self.existsInLocalStorage('projectNames')) {
                projectNamesSet = new Set(self.getFromLocalStorage('projectNames'));
            } else {
                projectNamesSet = new Set([]);
            }
            projectNamesSet.add('stir_fry_' + projectName);
            self.saveToLocalStorage('projectNames', Array.from(projectNamesSet));
        }
    }

    self.loadProjectFromLocalStorage = function(projectName) {
        if (projectName != undefined) {
            console.log('LOADING FROM LOCAL STORAGE', projectName);
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
        if (!self.existsInLocalStorage('abouted') || self.getFromLocalStorage('abouted') == false) {

            console.log('Showing "About" to first time visitors!');
            $('#about-window').show();
            self.saveToLocalStorage('abouted', true);
        }
        fetch('/get-stir-fry-ingredients', {
            method: 'get'
        }).then(function(response) {
            if (!response.ok) {
                throw Error(response.statusText);
            }
            return response;
        }).then(function(response) {
            return response.json();
        }).then(function(ingredients) {
            self.ingredients = []
            ingredients.forEach(function(ingredient) {
                var stirFryIngredient = new StirFryIngredient(self, ingredient);
                self.ingredients.push(stirFryIngredient);
                self.presentSet.add(stirFryIngredient);
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
        }).catch(function(error) {
            console.log(error);
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
                name = name.split('stir_fry_').slice(1).join('');
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
        var message = '';
        var projectNames;
        if (self.existsInLocalStorage('projectNames')) {
            projectNames = self.getFromLocalStorage('projectNames');
            message += 'Saved projects:\n';
            self.getFromLocalStorage('projectNames').forEach(function(name) {
                name = name.split('stir_fry_').slice(1).join('');
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
            if (!projectNameSet.has('stir_fry_'+projectName)) {
                alert('Project not found, please try again.')
            } else {
                self.loadProjectFromLocalStorage(projectName);
                console.log('LOADED');
                self.saveProjectToLocalStorage('');
            }
        }
    });

    $('#about').click(function() {
        $('#recipe-window').hide();
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

    self.generating = false;

    self.generate = function() {
        if (!self.generating) {
            $('#generating').show();
            fetch('/generate-stir-fry', {
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
                if (!response.ok) {
                    throw Error(response.statusText);
                }
                return response;
            }).then(function(response) {
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
                });
                self.selectedSet = new Set(self.getIngredientsFromNames(selectedNames));
                self.lockedSet = new Set(self.getIngredientsFromNames(lockedNames));

                self.ingredients.forEach(function(ingredient) {
                    ingredient.render();
                });

                $('#generating').hide();
                self.generating = false;
                self.saveProjectToLocalStorage('');
            }).catch(function(error) {
                console.log(error);
                alert('Sorry, that didn\'t work. Please try re-loading or waiting for a bit.');
                $('#generating').hide();
                self.generating = false;
            });
        } else {
            console.log('Already generating.');
        }
    }

    $('#generate').click(function() {
        self.generate();
    });

    $('body').keydown(function(event){
        if (event.keyCode == 32) {
            $(document.activeElement).blur();
            self.generate();
        }
    });

    $('#recipe').click(function() {
        var earlyNames = [];
        var earlyMidNames = [];
        var earlyMidLateNames = [];
        var midNames = [];
        var midLateNames = [];
        var midLateFlavoringNames = [];
        var lateNames = [];
        var lateFlavoringNames = [];
        var flavoringNames = [];

        self.selectedSet.forEach(function(ingredient) {
            console.log('ingredient', ingredient.name)
            if (ingredient.data.stir_fry_early == 'y') {
                if (ingredient.data.stir_fry_mid == 'y') {
                    if (ingredient.data.stir_fry_late == 'y') {
                        earlyMidLateNames.push(ingredient.name);
                    } else {
                        earlyMidNames.push(ingredient.name);
                    }
                } else {
                    earlyNames.push(ingredient.name);
                }
            } else if (ingredient.data.stir_fry_mid == 'y') {
                if (ingredient.data.stir_fry_late == 'y') {
                    if (ingredient.data.stiri_fry_garnish == 'y') {
                        midLateFlavoringNames.push(ingredient.name);
                    } else {
                            midLateNames.push(ingredient.name);
                    }
                } else {
                    midNames.push(ingredient.name);
                }
            } else if (ingredient.data.stir_fry_late == 'y') {
                if (ingredient.data.stir_fry_garnish == 'y') {
                    lateFlavoringNames.push(ingredient.name);
                } else {
                    lateNames.push(ingredient.name);
                }
            } else if (ingredient.data.stir_fry_garnish == 'y') {
                flavoringNames.push(ingredient.name);
            }
        });

        var html = '';
        if (Array.from(self.selectedSet).length > 1) {
            earlyNames.forEach(function(name) {
                html += '<li>[early] ' + name + '</li>';
            });
            earlyMidNames.forEach(function(name) {
                html += '<li>[early-mid] ' + name + '</li>';
            });
            earlyMidLateNames.forEach(function(name) {
                html += '<li>[early-mid-late] ' + name + '</li>';
            });
            midNames.forEach(function(name) {
                html += '<li>[mid] ' + name + '</li>';
            });
            midLateNames.forEach(function(name) {
                html += '<li>[mid-late] ' + name + '</li>';
            });
            midLateFlavoringNames.forEach(function(name) {
                html += '<li>[mid-late-flavoring] ' + name + '</li>';
            });
            lateNames.forEach(function(name) {
                html += '<li>[late] ' + name + '</li>';
            });
            lateFlavoringNames.forEach(function(name) {
                html += '<li>[late-flavoring] ' + name + '</li>';
            });
            flavoringNames.forEach(function(name) {
                html += '<li>[flavoring] ' + name + '</li>';
            });
        } else {
            html += '<li>You haven\'t selected any ingredients! This won\'nt be much of a stir fry, will it?</li>'
        }

        $('#ingredients-list').html(html);
        $('#about-window').hide();
        $('#recipe-window').show();
    });

    $('#recipe-close').click(function() {
        $('#recipe-window').hide();
        $('#ingredients-list').html('')
    });
}
