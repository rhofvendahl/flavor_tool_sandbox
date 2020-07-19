var SaladManager = function() {
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
            self.saveToLocalStorage(projectName, data);

            var projectNamesSet;
            if (self.existsInLocalStorage('projectNames')) {
                projectNamesSet = new Set(self.getFromLocalStorage('projectNames'));
            } else {
                projectNamesSet = new Set([]);
            }
            projectNamesSet.add('salad_' + projectName);
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
        fetch('/get-salad-ingredients', {
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
                var saladIngredient = new SaladIngredient(self, ingredient);
                self.ingredients.push(saladIngredient);
                self.presentSet.add(saladIngredient);
            });

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
                name = name.split('salad_').slice(1).join('');
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
                name = name.split('salad_').slice(1).join('');
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
            if (!projectNameSet.has('salad_'+projectName)) {
                alert('Project not found, please try again.')
            } else {
                self.loadProjectFromLocalStorage(projectName);
                console.log('LOADED');
                self.saveProjectToLocalStorage('');
            }
        }
    });

    // $('#about-window').hide();
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
            self.generating = true;
            fetch('/generate-salad', {
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
            console.log('Already generating.')
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
        console.log('clicked')
        var leafyGreenNames = [];
        var extraNames = [];
        var extraVegNames = [];
        var extraFruitNames = [];
        var extraNutSeedNames = [];
        var extraOtherNames = [];
        var dressingNames = [];
        var dressingOilNames = [];
        var dressingVinegarNames = [];
        var dressingSaltNames = [];
        var dressingPepperNames = [];

        self.selectedSet.forEach(function(ingredient) {
            // console.log('name', ingredient.name, ingredient.data);
            if (ingredient.data.salad_green == 'y') {
                // console.log('leafy green')
                leafyGreenNames.push(ingredient.name);
            } else if (ingredient.data.salad_extra == 'y') {
                // console.log('extra')
                extraNames.push(ingredient.name);
                if (ingredient.data.salad_extra_veg == 'y') {
                    extraVegNames.push(ingredient.name);
                } else if (ingredient.data.salad_extra_fruit == 'y') {
                    extraFruitNames.push(ingredient.name);
                } else if (ingredient.data.salad_extra_nut_seed == 'y') {
                    extraNutSeedNames.push(ingredient.name);
                } else {
                    extraOtherNames.push(ingredient.name);
                }
            } else if (ingredient.data.salad_dressing == 'y') {
                // console.log('dressing')
                dressingNames.push(ingredient.name);
                if (ingredient.data.salad_dressing_oil == 'y') {
                    dressingOilNames.push(ingredient.name);
                } else if (ingredient.data.salad_dressing_vinegar == 'y') {
                    dressingVinegarNames.push(ingredient.name);
                } else if (ingredient.data.salad_dressing_salt == 'y') {
                    dressingSaltNames.push(ingredient.name);
                } else if (ingredient.data.salad_dressing_pepper == 'y') {
                    dressingPepperNames.push(ingredient.name);
                }
            }
        });
        // console.log('LEAFY GREEN NAMES', leafyGreenNames); //empty
        // console.log('EXTRA NAMES', extraNames); //115
        // console.log('DRESSING NAMES', dressingNames); //21
        var leafyGreensHtml = '<li>Leafy greens</li><ul>';
        if (leafyGreenNames.length > 0) {
            // console.log('leafy greens long enough', leafygreenNames)
            leafyGreenNames.forEach(function(name) {
                leafyGreensHtml += '<li>' + name + '</li>';
            });
        } else {
            leafyGreensHtml += '<li>Oh no! You haven\'nt selected any leafy greens. You\'ll need to go back and add some before you can make a tasty salad.</li>';
        }
        leafyGreensHtml += '</ul>'

        var extrasHtml = '<li>Extras</li><ul>';
        if (extraNames.length > 0) {
            extraNames.forEach(function(name) {
                extrasHtml += '<li>' + name + '</li>';
            });
        } else {
            extrasHtml += '<li>You haven\'nt selected any salad extras. You\'ll probably want to go back and add some, or your salad might not be very interesting.</li>';
        }
        extrasHtml += '</ul>'

        var dressingHtml = '<li>Dressing</li><ul>';
        if (dressingNames.length > 0) {
            // console.log('dressing long enough')
            if (dressingOilNames.length > 0) {
                // console.log('some oil names')
                dressingOilNames.forEach(function(name) {
                    dressingHtml += '<li>(~1 tbs/serving) ' + name + '</li>';
                });
            } else {
                dressingHtml += '<li>You haven\'nt added a dressing oil. I suspect the salad would taste better if you go back and add one!</li>';
            }
            if (dressingVinegarNames.length > 0) {
                // console.log('some vinegar')
                dressingVinegarNames.forEach(function(name) {
                    dressingHtml += '<li>(~.5 tbs/serving) ' + name + '</li>';
                });
            } else {
                dressingHtml += '<li>You haven\'nt added a dressing vinegar. Without vinegar, your salad will probably taste lopsided; you might want to go back and add one.</li>';
            }
            if (dressingSaltNames.length > 0) {
                // console.log('some salt')
                dressingSaltNames.forEach(function(name) {
                    dressingHtml += '<li>(~a pinch/serving) ' + name + '</li>';
                });
            } else {
                dressingHtml += '<li>You haven\'nt added a salt. This one\'s kinda optional, but I\'d strongly suggest you at least try adding salt to a salad or two.</li>';
            }
            if (dressingPepperNames.length > 0) {
                // console.log('some pepper')
                dressingPepperNames.forEach(function(name) {
                    dressingHtml += '<li>(~1/4 tsp/serving) ' + name + '</li>';
                });
            } else {
                dressingHtml += '<li>You haven\'nt added a dressing pepper. Pepper isn\'t as crucial as some other ingredients, but I\'d strongly recommend at least trying it a few times.</li>';
            }
        } else {
            dressingHtml += '<li>You haven\'nt selected any dressing ingredients at all! I suspect your salad will be pretty dry without dressing...</li>';
        }
        dressingHtml += '</ul>';
        // console.log('leafygreenshtml', leafyGreensHtml);
        // console.log('extrashtml', extrasHtml);
        // console.log('dressingHtml', dressingHtml);
        $('#ingredients-list').html(leafyGreensHtml + extrasHtml + dressingHtml);
        $('#about-window').hide();
        $('#recipe-window').show();
    });

    $('#recipe-close').click(function() {
        $('#recipe-window').hide();
        $('#ingredients-list').html('')
    });
}
