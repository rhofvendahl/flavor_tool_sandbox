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
            },
            title: ''
        },
        physics: {
            maxVelocity: 5
        },
        interaction: {
            tooltipDelay: 1200
        },
        edges: {
            chosen: false
        }
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
            projectNamesSet.add('salad_' + projectName);
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
            console.log(self.nodes.getIds()[0])
            self.network.fit({
                nodes: highlightedNames,
                animation: true
            });
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
                    ingredient.add();
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
        }
        ingredient.render();
        self.saveProjectToLocalStorage('');
    }

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
        }
        ingredient.render()
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
            self.endMenuTimeout = setTimeout(function() { // should be cleared and set to null at this time
                self.endMenu();
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
                ingredient.add();
                // ingredient.render();
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

    self.generate = function() {
        if (!self.generating) {
            self.generating = true;
            $('#generating').show();
            console.log('about to fetch')
            fetch('/generate-salad', {
                method: 'post',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    // present: self.getNamesFromSet(self.presentSet),
                    // locked: self.getNamesFromSet(self.lockedSet)
                    present: self.getPresentNames(),
                    locked: self.getLockedNames()
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

                $('#generating').hide();
                self.generating = false;
                self.saveProjectToLocalStorage('');

                setTimeout(function() {
                    self.network.fit({
                        nodes: selectedNames,
                        animation: true
                    });
                }, 2000);
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
        var spacebar = event.keyCode == 32;
        var activeElement = $(document.activeElement);
        var searching = activeElement.hasClass('selectivity-multiple-input');
        var emptySearch = $('.selectivity-multiple-input').val() == '';
        if (spacebar && (!searching || emptySearch)) {
            $('#present').selectivity('close');
            activeElement.blur()
            self.generate();
        }
    });

    $('#recipe').click(function() {
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

        self.getSelectedSet().forEach(function(ingredient) {
            if (ingredient.data.salad_green == 'y') {
                leafyGreenNames.push(ingredient.name);
            } else if (ingredient.data.salad_extra == 'y') {
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
        var leafyGreensHtml = '<li>Leafy greens</li><ul>';
        if (leafyGreenNames.length > 0) {
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
            if (dressingOilNames.length > 0) {
                dressingOilNames.forEach(function(name) {
                    dressingHtml += '<li>(~1 tbs/serving) ' + name + '</li>';
                });
            } else {
                dressingHtml += '<li>You haven\'nt added a dressing oil. I suspect the salad would taste better if you go back and add one!</li>';
            }
            if (dressingVinegarNames.length > 0) {
                dressingVinegarNames.forEach(function(name) {
                    dressingHtml += '<li>(~.5 tbs/serving) ' + name + '</li>';
                });
            } else {
                dressingHtml += '<li>You haven\'nt added a dressing vinegar. Without vinegar, your salad will probably taste lopsided; you might want to go back and add one.</li>';
            }
            if (dressingSaltNames.length > 0) {
                dressingSaltNames.forEach(function(name) {
                    dressingHtml += '<li>(~a pinch/serving) ' + name + '</li>';
                });
            } else {
                dressingHtml += '<li>You haven\'nt added a salt. This one\'s kinda optional, but I\'d strongly suggest you at least try adding salt to a salad or two.</li>';
            }
            if (dressingPepperNames.length > 0) {
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
        $('#ingredients-list').html(leafyGreensHtml + extrasHtml + dressingHtml);
        $('#about-window').hide();
        $('#recipe-window').show();
    });

    $('#recipe-close').click(function() {
        $('#recipe-window').hide();
        $('#ingredients-list').html('')
    });
}
