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
                size: 12,
            },
            title: '',
            shapeProperties: {
                interpolation: false, // should be unnecessary, but might help with leak
            },
        },
        physics: {
            // maxVelocity: 20,
            timestep: .25,
            barnesHut: {
              gravitationalConstant: -3000,
              centralGravity: 0.2,
              springLength: 150,
              springConstant: 0.03,
            },
        },
        interaction: {
            tooltipDelay: 1200,
        },
        edges: {
            chosen: false,
            smooth: {
                type: 'continuous',
            },
            // length: 200,
        },
    };
    self.network = new vis.Network(container, data, options);

    self.ingredients = [];

    self.getPresentSet = function() {
        var presentSet = new Set();
        self.ingredients.forEach(function(ingredient) {
            if (ingredient.present) {
                presentSet.add(ingredient);
            }
        });
        return presentSet;
    }

    self.getSelectedSet = function() {
        var selectedSet = new Set();
        self.ingredients.forEach(function(ingredient) {
            if (ingredient.selected) {
                selectedSet.add(ingredient);
            }
        });
        return selectedSet;
    }

    self.getLockedSet = function() {
        var lockedSet = new Set();
        self.ingredients.forEach(function(ingredient) {
            if (ingredient.locked) {
                lockedSet.add(ingredient);
            }
        });
        return lockedSet;
    }

    self.getConnectedSet = function() {
        var connectedSet = new Set();
        self.ingredients.forEach(function(ingredient) {
            if (ingredient.connected) {
                connectedSet.add(ingredient);
            }
        });
        return connectedSet;
    }

    self.getPresentNames = function() {
        var presentNames = [];
        self.ingredients.forEach(function(ingredient) {
            if (ingredient.present) {
                presentNames.push(ingredient.name);
            }
        });
        return presentNames;
    }

    self.getSelectedNames = function() {
        var selectedNames = [];
        self.ingredients.forEach(function(ingredient) {
            if (ingredient.selected) {
                selectedNames.push(ingredient.name);
            }
        });
        return selectedNames;
    }

    self.getLockedNames = function() {
        var lockedNames = [];
        self.ingredients.forEach(function(ingredient) {
            if (ingredient.locked) {
                lockedNames.push(ingredient.name);
            }
        });
        return lockedNames;
    }

    self.getConnectedNames = function() {
        var connectedNames = [];
        self.ingredients.forEach(function(ingredient) {
            if (ingredient.connected) {
                connectedNames.push(ingredient.name);
            }
        });
        return connectedNames;
    }

    self.getHighlightedNames = function() {
        var highlightedNames = [];
        self.ingredients.forEach(function(ingredient) {
            if (ingredient.highlighted) {
                highlightedNames.push(ingredient.name);
            }
        });
        return highlightedNames;
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
                presentArray: self.getPresentNames(),
                selectedArray: self.getSelectedNames(),
                lockedArray: self.getLockedNames(),
                connectedArray: self.getConnectedNames()
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
                var presentSet = new Set(self.getIngredientsFromNames(data.presentArray));
                var selectedSet = new Set(self.getIngredientsFromNames(data.selectedArray));
                var lockedSet = new Set(self.getIngredientsFromNames(data.lockedArray));
                var connectedSet = new Set(self.getIngredientsFromNames(data.connectedArray));
                self.ingredients.forEach(function(ingredient) {
                    if (presentSet.has(ingredient)) {
                        ingredient.add({
                            selected: selectedSet.has(ingredient),
                            locked: lockedSet.has(ingredient),
                            connected: connectedSet.has(ingredient)
                        });
                    } else {
                        ingredient.clear();
                    }
                });
            } else {
                console.log('no data found in localStorage')
            }
        }
    }

    // unintuitive, needs refactoring
    self.highlightMatches = function(query) {
        var highlighted = [];
        self.ingredients.forEach(function(ingredient) {
            if (ingredient.present) {
                if (ingredient.name.toLowerCase().includes(query.toLowerCase()) && query != '') { // should be highlighted
                    if (!ingredient.highlighted) {
                        ingredient.highlighted = true;
                        ingredient.render();
                    }
                } else { // shouldn't be highlighted
                    if (ingredient.highlighted) {
                        ingredient.highlighted = false;
                        ingredient.render();
                    }
                }
            }
        });
        var highlightedNames = self.getHighlightedNames();
        if (highlightedNames.length > 0) {
            self.network.fit({
                nodes: highlightedNames,
                animation: true
            });
        }
    }

    self.load = function() {
        console.log('showing loading')
        $('#loading').show();

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
            console.log('hiding loading')
            $('#loading').hide();
            self.ingredients = []
            ingredients.forEach(function(ingredient) {
                var stirFryIngredient = new StirFryIngredient(self, ingredient);
                self.ingredients.push(stirFryIngredient);
            });

            $('#present').selectivity({
                items: self.getIngredientNames(),
                multiple: true,
                inputType: 'Multiple',
                placeholder: 'Search ingredients'
            });

            $('#present').on('change', function(event) {
                var selectivityContainer = $('.selectivity-multiple-input-container')
                selectivityContainer.scrollTop(selectivityContainer.prop("scrollHeight"));
                $('.selectivity-multiple-input').attr('placeholder', 'Search ingredients');

                if (event.added && typeof(event.added) == 'object') {
                    var ingredient = self.getFromName(event.added.id);
                    ingredient.present = true;
                    ingredient.render();
                } else if (event.removed && typeof(event.removed) == 'object') {
                    var ingredient = self.getFromName(event.removed.id);
                    ingredient.clear();
                }
            });

            // kludge-y
            // couldn't get event to fire when selectivity input changed directly
            $('.selectivity-multiple-input').keyup(function(event) {
                var query = $('.selectivity-multiple-input').val();
                self.highlightMatches(query);
            });

            // SUUUPER kludge-y, not gonna even explain
            var selectivityInput = $('.selectivity-multiple-input').first();
            selectivityInput.addClass('form-control');
            selectivityInput.addClass('mt-3');

            selectivityInput.css({
                border: '1px solid #6C757D',
                borderRadius: '8px',
                backgroundColor: 'white',
                position: 'absolute',
                bottom: '0px',
                right: '0px',
                left: '0px'
            })

            if (self.existsInLocalStorage('')) {
                console.log('CACHE FOUND');
                self.loadProjectFromLocalStorage('');
            } else {
                self.ingredients.forEach(function(ingredient) {
                    ingredient.add();
                });
            }

            setTimeout(function() {
                self.network.fit({
                    nodes: self.getSelectedNames(),
                    animation: true,
                });
            }, 2600);
        }).catch(function(error) {
            console.log(error);
        });
    };


    self.clickTimeout = null;

    self.toggleSelect = function(ingredient) {
        if (ingredient.selected) {
            if (ingredient.locked) {
                ingredient.locked = false;
            }
            ingredient.selected = false;
        } else {
            ingredient.selected = true;
            gtag('event', 'ingredient_select', {
                'event_category': 'ingredient',
                'event_label': 'Select Ingredient: ' + ingredient.name,
                'non_interaction': true,
            });
        }
        ingredient.render();
        self.saveProjectToLocalStorage('');
    }

    self.network.on('hold', function() {
        clearTimeout(self.clickTimeout);
        self.clickTimeout = null;
    });

    self.network.on('click', function(properties) {
        $('#present').selectivity('close');
        $('.selectivity-multiple-input').attr('placeholder', 'Search ingredients');
        $(document.activeElement).blur()

        if (self.clickTimeout) {
            clearTimeout(self.clickTimeout);
            self.clickTimeout = null;
        } else {
            self.clickTimeout = setTimeout(function() {
                if (properties.nodes.length > 0) {
                    var ingredient = self.getFromName(properties.nodes[0]);
                    self.toggleSelect(ingredient);
                }
                self.clickTimeout = null;
            }, 250);
        }
    });

    self.toggleLock = function(ingredient) {
        if (!ingredient.selected) {
            ingredient.selected = true;
        }
        if (ingredient.locked) {
            ingredient.locked = false;
        } else {
            ingredient.locked = true;
            gtag('event', 'ingredient_lock', {
                'event_category': 'ingredient',
                'event_label': 'Lock Ingredient: ' + ingredient.name,
                'non_interaction': true,
            });
        }
        ingredient.render();
        self.saveProjectToLocalStorage('');
    }

    self.network.on('doubleClick', function(properties) {
        if (properties.nodes.length > 0) {
            var ingredient = self.getFromName(properties.nodes[0]);
            self.toggleLock(ingredient);
        }
    });

    $('#network').contextmenu(function() {
        return false;
    });

    self.toggleConnect = function(ingredient) {
        if (ingredient.connected) {
            ingredient.connected = false;
        } else {
            ingredient.connected = true;
            gtag('event', 'ingredient_connect', {
                'event_category': 'ingredient',
                'event_label': 'Connect Ingredient: ' + ingredient.name,
                'non_interaction': true,
            });
        }
        ingredient.render();
        self.saveProjectToLocalStorage('');
    }

    self.network.on('oncontext', function(properties) {
        var id = self.network.getNodeAt({x: properties.pointer.DOM.x, y: properties.pointer.DOM.y});
        if (id != undefined) {
            var ingredient = self.getFromName(id);
            self.toggleConnect(ingredient);
        }
    });

// WAAAAAAAAAAAAAAAAAAAAAAAAAAAAAY OVERCOMPLICATED
// When I designed this section I thought the menu would be elsewhere, and the mouse would need time to get there
// If I were to re-do it I'd just make an invisible div appear over the mouse and including a menu to the right, that'd hide when the mouse left it.
    self.menuId = null;
    self.endMenuTimeout = null;
    self.mouseOnNode = false;

    self.renderMenuButtons = function() {
        var ingredient = self.getFromName(self.menuId);
        if (ingredient.selected) {
            $('#select').removeClass('btn-primary');
            $('#select').addClass('btn-light');
            $('#select').text('Unselect');
        } else {
            $('#select').removeClass('btn-light');
            $('#select').addClass('btn-primary');
            $('#select').text('Select');
        }
        if (ingredient.locked) {
            $('#lock').removeClass('btn-primary');
            $('#lock').addClass('btn-light');
            $('#lock').text('Unlock');
        } else {
            $('#lock').removeClass('btn-light');
            $('#lock').addClass('btn-primary');
            $('#lock').text('Lock');
        }
        if (ingredient.connected) {
            $('#connect').removeClass('btn-primary');
            $('#connect').addClass('btn-light');
            $('#connect').text('Unconnect');
        } else {
            $('#connect').removeClass('btn-light');
            $('#connect').addClass('btn-primary');
            $('#connect').text('Connect');
        }
    }

    $('#remove').click(function() {
        var ingredient = self.getFromName(self.menuId);
        self.endMenu();
        ingredient.clear();
        self.saveProjectToLocalStorage('');
    })

    $('#select').click(function() {
        var ingredient = self.getFromName(self.menuId);
        self.toggleSelect(ingredient);
        self.renderMenuButtons();
    });

    $('#lock').click(function() {
        var ingredient = self.getFromName(self.menuId);
        self.toggleLock(ingredient);
        self.renderMenuButtons();
    })

    $('#connect').click(function() {
        var ingredient = self.getFromName(self.menuId);
        self.toggleConnect(ingredient);
        self.renderMenuButtons();
    });

    self.startMenu = function(menuId) {
        self.menuId = menuId;
        var ingredient = self.getFromName(self.menuId);
        ingredient.menu = true;
        var canvasPosition = self.network.getPositions(menuId)[menuId];
        var domPosition = self.network.canvasToDOM(canvasPosition);
        $('#menu-wrapper').css({
            top: domPosition.y,
            left: domPosition.x
        })
        self.renderMenuButtons();
        $('#menu-wrapper').show();
        self.network.selectNodes([menuId]);
        self.getFromName(self.menuId).render();

        self.endMenuTimeout = setTimeout(function() { // should be cleared and set to null at this time
            self.endMenu();
            clearTimeout(self.endMenuTimeout); // just to be safe
            self.endMenuTimeout = null;
        }, 5000); // how long it takes menu to disappear
    }

    self.endMenu = function() {
        self.network.unselectAll();
        if (self.menuId) {
            var ingredient = self.getFromName(self.menuId);
            var size = self.nodes.get(self.menuId).size - 5;
            self.nodes.update({
                id: self.menuId,
                size: size
            });
            ingredient.menu = false;
            ingredient.render();
            self.menuId = null;
        }
        $('#menu-wrapper').hide();
        $('#menu-wrapper').css({
            left: 0,
            top: 0
        })
    }

    self.network.on('showPopup', function(menuId) {
        self.mouseOnNode = true;

        if (self.endMenuTimeout) { // either because mouse has returned to hoverNode, or because mouse is at a new node and the old is to be dehovered
            clearTimeout(self.endMenuTimeout);
        }
        if (self.menuId && self.menuId != menuId) {
            self.endMenu();
        }
        if (self.menuId != menuId) {
            self.startMenu(menuId);
        }
    });

    self.network.on('hidePopup', function() {
        if (self.mouseOnNode) {
            self.mouseOnNode = false;
            clearTimeout(self.endMenuTimeout);
            self.endMenuTimeout = setTimeout(function() { // should be cleared and set to null at this time
                self.endMenu();
                clearTimeout(self.endMenuTimeout); // just to be safe
                self.endMenuTimeout = null;
            }, 300); // how long it takes menu to disappear
        }
    });

    $('#menu-wrapper').hover(function() {
        if (self.endMenuTimeout) {
            clearTimeout(self.endMenuTimeout);
            self.endMenuTimeout = null;
        }
    }, function() {
        self.endMenu();
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

            var selectedNamesString = self.getSelectedNames().join(' + ');
            gtag('event', 'project_save', {
                'event_category': 'project',
                'event_label': 'Save Stir-Fry ' + projectName + ': ' + selectedNamesString,
                'non_interaction': true,
            });
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

                var selectedNamesString = self.getSelectedNames().join(' + ');
                gtag('event', 'project_load', {
                    'event_category': 'project',
                    'event_label': 'Load Stir-Fry ' + projectName + ': ' + selectedNamesString,
                    'non_interaction': true,
                });
            }
        }
    });

    $('#about').click(function() {
        if ($('#about-window').is(':hidden')) {
            $('#recipe-window').hide();
            $('#about-window').show();
        } else {
            $('#about-window').hide();
        }
    });

    $('#about-close').click(function() {
        $('#about-window').hide();
    });

    $('#all').click(function() {
        var confirmation = prompt('Are you sure? (y/n)');
        if (confirmation == 'y') {
            self.ingredients.forEach(function(ingredient) {
                ingredient.add();
            });
            self.saveProjectToLocalStorage('');
        }
    });

    $('#none').click(function() {
        var confirmation = prompt('Are you sure? (y/n)');
        if (confirmation == 'y') {
            self.ingredients.forEach(function(ingredient) {
                ingredient.clear();
            });
            self.saveProjectToLocalStorage('');
        }
    });

    self.generating = false;
    self.default_method = 'reliable';
    self.generate = function(method) {
        // console.log('GENERATING')
        if (!self.generating) {
            gtag('event', 'generate_start', {
                'event_category': 'generate',
                'event_label': 'Start ' + method.toUpperCase() + ' Stir-Fry',
                'non_interaction': true,
            });
            // console.log('not already generating')
            self.generating = true;
            $('#generating').show();
            self.default_method = method;
            url = (method == 'fun') ? '/generate-stir-fry' : '/generate-stir-fry-black-magic';
            fetch(url, {
                method: 'post',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    present: self.getPresentNames(),
                    locked: self.getLockedNames()
                })
            }).then(function(response) {
                // console.log('dealing with response errors')
                if (!response.ok) {
                    throw Error(response.statusText);
                }
                return response;
            }).then(function(response) {
                // console.log('dealing with response')
                return response.json();
            }).then(function(json) {
                $('#generating').hide();
                self.generating = false;

                if (json['outcome'] == 'success') {
                    // console.log('dealing with json')
                    var presentNames = json['data']['present_names'];
                    var selectedNames = json['data']['selected_names'];
                    var lockedNames = json['data']['locked_names'];
                    var generatedNames = json['data']['generated_names'];

                    var presentNamesSet = new Set(presentNames);
                    var selectedNamesSet = new Set(selectedNames);
                    var lockedNamesSet = new Set(lockedNames);
                    var generatedNamesset = new Set(generatedNames);

                    self.ingredients.forEach(function(ingredient) {
                        if (presentNamesSet.has(ingredient.name) && !ingredient.present) {
                            ingredient.add({
                                selected: selectedNamesSet.has(ingredient.name),
                                locked: lockedNamesSet.has(ingredient.name),
                                connected: false
                            });
                            // self.getPresentSet().add(ingredient);
                        } // no else clause, as I don't want to remove any ingredients added since the request was sent
                        ingredient.selected = selectedNamesSet.has(ingredient.name);
                        ingredient.locked = lockedNamesSet.has(ingredient.name);
                        ingredient.render();
                    });

                    self.saveProjectToLocalStorage('');

                    setTimeout(function() {
                        self.network.fit({
                            nodes: selectedNames,
                            animation: true
                        });
                    }, 2200);

                    if (!self.existsInLocalStorage('reciped') || self.getFromLocalStorage('reciped') == false) {
                        console.log('Showing "Recipe" to first time generators!');
                        $('#about-window').show();
                        $('#recipe').click();
                        self.saveToLocalStorage('reciped', true);
                    }

                    gtag('event', 'generate_success', {
                        'event_category': 'generate',
                        'event_label': method.toUpperCase() + ' Stir-Fry Success',
                        'non_interaction': true,
                    });
                } else if (json['outcome'] == 'failure') {
                    if (json['message']) {
                        alert(json['message']);
                    } else {
                        console.log('ERROR: received "failure" outcome but no message')
                    }

                    gtag('event', 'generate_failure', {
                        'event_category': 'generate',
                        'event_label': method.toUpperCase() + ' Stir-Fry Failure',
                        'non_interaction': true,
                    });
                } else {
                    console.log('ERROR: received outcome other than "success" or "failure"');
                }
                // gtag('event', 'generate_success', {
                //
                // })
                // ga('send', 'event', 'generate', 'success', method);
            }).catch(function(error) {
                console.log(error);
                alert('Sorry, that didn\'t work. Please try re-loading or waiting for a bit.');
                $('#generating').hide();
                self.generating = false;
                // ga('send', 'event', 'generate', 'failure', method);
            });
        } else {
            console.log('Already generating.');
        }
    }

    $('#generate-fun').click(function() {
        self.generate('fun');
    });

    $('#generate-reliable').click(function() {
        self.generate('reliable');
    });

    $('body').keydown(function(event){
        var spacebar = event.keyCode == 32;
        var activeElement = $(document.activeElement);
        var searching = activeElement.hasClass('selectivity-multiple-input');
        var emptySearch = $('.selectivity-multiple-input').val() == '';
        if (spacebar && (!searching || emptySearch)) {
            $('#present').selectivity('close');
            activeElement.blur()
            self.generate(self.default_method);
        }
    });

    $('#recipe').click(function() {
        if ($('#recipe-window').is(':hidden')) {
            var earlyNames = [];
            var earlyMidNames = [];
            var earlyMidLateNames = [];
            var midNames = [];
            var midLateNames = [];
            var midLateFlavoringNames = [];
            var lateNames = [];
            var lateFlavoringNames = [];
            var flavoringNames = [];

            self.getSelectedSet().forEach(function(ingredient) {
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
            if (Array.from(self.getSelectedSet()).length > 1) {
                earlyNames.forEach(function(name) {
                    html += '<li>[early] <strong>' + name + '</strong></li>';
                });
                earlyMidNames.forEach(function(name) {
                    html += '<li>[early or mid] <strong>' + name + '</strong></li>';
                });
                earlyMidLateNames.forEach(function(name) {
                    html += '<li>[early or mid or late] <strong>' + name + '</strong></li>';
                });
                midNames.forEach(function(name) {
                    html += '<li>[mid] <strong>' + name + '</strong></li>';
                });
                midLateNames.forEach(function(name) {
                    html += '<li>[mid or late] <strong>' + name + '</strong></li>';
                });
                midLateFlavoringNames.forEach(function(name) {
                    html += '<li>[mid or late or flavoring] <strong>' + name + '</strong></li>';
                });
                lateNames.forEach(function(name) {
                    html += '<li>[late] <strong>' + name + '</strong></li>';
                });
                lateFlavoringNames.forEach(function(name) {
                    html += '<li>[late or flavoring] <strong>' + name + '</strong></li>';
                });
                flavoringNames.forEach(function(name) {
                    html += '<li>[flavoring] <strong>' + name + '</strong></li>';
                });
            } else {
                html += '<li>You haven\'t selected any ingredients! This won\'nt be much of a stir fry, will it?</li>'
            }

            $('#ingredients-list').html(html);
            $('#about-window').hide();
            $('#recipe-window').show();
        } else {
            $('#recipe-window').hide();
            $('#ingredients-list').html('')
        }
    });

    $('#recipe-close').click(function() {
        $('#recipe-window').hide();
        $('#ingredients-list').html('')
    });
}
