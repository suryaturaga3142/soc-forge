`timescale 1ns/10ps

/* verilator coverage_off */

module {{module_name}}_tb;

// Parameters
localparam CLK_PERIOD = 10;

logic clk, n_rst;

{{module_name}} #() DUT (.*);

// clockgen
always begin
    clk = 0;
    #(CLK_PERIOD / 2.0);
    clk = 1;
    #(CLK_PERIOD / 2.0);
end

task reset_dut;
begin
    n_rst = 0;
    @(posedge clk);
    @(posedge clk);
    @(negedge clk);
    n_rst = 1;
    @(negedge clk);
    @(negedge clk);
end
endtask

initial begin
    #10000 $display("Simulation timeout reached");
    $finish;
end

initial begin
    reset_dut();

    // Testbench

    $dumpfile("dump_{{block}}_{{module_name}}_tb.vcd");
    $dumpvars(0, {{module_name}}_tb);
    $finish;
end

endmodule

/* verilator coverage_on */

