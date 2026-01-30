/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { MrpDisplayRecord } from "@mrp_workorder/mrp_display/mrp_display_record";

patch(MrpDisplayRecord.prototype, {
    async produce_without_backorder() {

        await this.model.orm.call(
            "mrp.production",
            "button_mark_partial_production",
            [this.resId] 
        );
        
        await this.model.load();
    },
});