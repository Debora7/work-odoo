/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { MrpRegisterProductionDialog } from "@mrp_workorder/mrp_display/dialog/mrp_register_production_dialog";

patch(MrpRegisterProductionDialog.prototype, {
    async produce_without_backorder() {
        const record = this.props.record;
        this.state.disabled = true;

        try {
            await record.save();

            const resModel = this.props.workorderId ? "mrp.workorder" : "mrp.production";
            const resId = [this.props.workorderId || record.resId];
            
            await record.model.orm.call(resModel, "set_qty_producing", [resId]);

            await record.model.orm.call(
                "mrp.production", 
                "button_mark_partial_production", 
                [record.resId],
                {
                    context: { ...record.context, 'from_shop_floor': true }
                }
            );

            await record.load(); 

            if (this.props.reload) {
                await this.props.reload(record);
            }
            
            this.props.close();
        } catch (error) {
            this.state.disabled = false;
            throw error;
        }
    },
});