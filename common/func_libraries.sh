#
#   2 Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#   3 Neither the names of the copyright holders nor the names of the
#   contributors may be used to endorse or promote products derived from this
#   software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#   =======================================================================

#define host libraries
host_libraries[0]="libpresenteragent.so"

declare -A host_map=()
host_map["libpresenteragent.so"]="${script_path}/presenter/agent"

#define device libraries
device_libraries[0]="libascend_ezdvpp.so"

declare -A device_map=()
device_map["libascend_ezdvpp.so"]="${script_path}/utils/ascend_ezdvpp"

function get_compilation_targets()
{
    compilation_target=$1
    if [[ ${compilation_target}"X" == "X" ]];then
        echo "${host_libraries[@]} ${device_libraries}"
        return 0
    fi
    
    denpendency_libs=""
    host_libs=`echo "${host_libraries[@]}" | grep "${compilation_target}"`
    host_running=$?
    if [[ host_running -eq 0 ]];then
        libs=`echo "${host_libraries[@]}" | awk -F '$compilation_target' '{print $1}'`
        denpendency_libs="${denpendency_libs} ${libs}"
    fi
    device_libs=`echo "${device_libraries[@]}" | grep "${compilation_target}"`
    device_running=$?
    if [[ device_running -eq 0 ]];then    
        libs=`echo "${device_libraries[@]}" | awk -F '$compilation_target' '{print $1}'`
        denpendency_libs="${denpendency_libs} ${libs}"
    fi
    
    if [[ host_running -ne 0 && device_running -ne 0 ]];then
        return 1
    fi
    echo ${denpendency_libs}
    return 0
}