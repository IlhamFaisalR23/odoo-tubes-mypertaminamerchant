odoo.define("pos_pertamina.category_form_restriction", function (require) {
    "use strict";

    var FormController = require("web.FormController");
    var viewRegistry = require("web.view_registry");
    var rpc = require("web.rpc");

    var CategoryFormController = FormController.extend({
        init: function () {
            this._super.apply(this, arguments);
            this.isRestricted = false;
        },

        willStart: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                return rpc.query({
                    model: "res.users",
                    method: "has_group",
                    args: ["pos_pertamina.group_admin_restricted"],
                }).then(function (result) {
                    self.isRestricted = result;
                });
            });
        },

        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                if (self.isRestricted) {
                    self._restrictFormFields();
                }
            });
        },

        _restrictFormFields: function () {
            var formEl = this.$el.find(".o_form_view");
            if (formEl.length) {
                var fieldsToDisable = ["parent_id", "property_cost_method", "type"];
                fieldsToDisable.forEach(function (fieldName) {
                    var input = formEl.find('[name="' + fieldName + '"]');
                    if (input.length) {
                        input.prop("disabled", true);
                        input.addClass("o_field_disabled");
                    }
                });
            }
        },
    });

    viewRegistry.add("category_form_restriction", CategoryFormController);
});
